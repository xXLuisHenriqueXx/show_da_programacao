import uuid
import json
from typing import Dict, Optional, List
from src.config.loader import ConfigLoader
from src.interfaces.llm import LLMClientInterface

class GameManager:
    def __init__(self):
        self.full_config = ConfigLoader.load_config()
        self.settings = self.full_config.get("settings", {})
        
        self.vector_store_id = self.settings.get("vector_store_id")
        self.static_questions: List[dict] = self.full_config.get("questions", [])
        
        self.games: Dict[str, dict] = {}

    def create_game(self) -> str:
        game_id = str(uuid.uuid4())
        self.games[game_id] = {
            "mode": "static",
            "current_question_index": 0,
            "accumulated_prize": 0,
            "status": "active",
            "generated_questions": [],
            "history": [],
            "chat_history": [] 
        }
        return game_id

    def get_game(self, game_id: str) -> Optional[dict]:
        return self.games.get(game_id)

    def get_current_question(self, game_id: str):
        game = self.get_game(game_id)
        if not game: return None
        
        if game['mode'] == 'static':
            source = self.static_questions
        else:
            source = game['generated_questions']

        idx = game['current_question_index']

        if idx >= len(source):
            if game['status'] == 'active':
                game['status'] = 'won'
            return "WIN"
            
        q = source[idx]
        return {
            "id": q["id"],
            "text": q["text"],
            "options": q["options"],
            "prize": q["prize"],
            "currency": self.settings.get("currency_symbol", "$")
        }

    def submit_answer(self, game_id: str, option_index: int) -> bool:
        game = self.get_game(game_id)
        if not game or game['status'] != 'active':
            return False

        if game['mode'] == 'static':
            questions = self.static_questions
        else:
            questions = game['generated_questions']

        idx = game['current_question_index']
        question_data = questions[idx]
        
        if option_index < 0 or option_index >= len(question_data['options']):
            return False

        selected = question_data['options'][option_index]
        correct = question_data['correct_option']
        
        game['history'].append({
            "question": question_data['text'],
            "selected": selected,
            "correct": correct,
            "result": "hit" if selected == correct else "miss"
        })

        if selected == correct:
            game['accumulated_prize'] += question_data['prize']
            game['current_question_index'] += 1
            return True
        else:
            game['status'] = 'lost'
            return False

    def generate_next_level(self, game_id: str, ai_client: LLMClientInterface):
        game = self.get_game(game_id)
        if not game: return False

        system_prompt = self.settings.get('tutor_question_generations_instructions', "")
        
        system_prompt += (
            "Você é um gerador de API de quiz. "
            "Gere 3 novas perguntas difíceis. "
            "A saída DEVE ser estritamente um JSON válido com a estrutura: "
            "{'questions': [{'id': 'gen_1', 'text': '...', 'options': ['A','B','C','D'], "
            "'correct_option': 'A', 'explanation': '...', 'prize': 10000}]}"
        )
        
        try:
            json_str = ai_client.generate_structured_content(
                system_prompt=system_prompt, 
                user_prompt="Gere o próximo nível.",
                vector_store_id=self.vector_store_id
            )
            
            clean_json = json_str.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            game['generated_questions'] = data.get('questions', [])
            game['mode'] = 'generated'
            game['current_question_index'] = 0
            game['status'] = 'active'
            return True
        except Exception as e:
            print(f"Erro ao gerar perguntas: {e}")
            return False

    def init_tutor_context(self, game_id: str):
        game = self.get_game(game_id)
        if not game: return

        status = game['status']
        history_str = json.dumps(game['history'], ensure_ascii=False)
        persona = self.settings.get("tutor_persona", "Você é um mentor sábio.")

        if status == 'lost':
            context = f"{persona} O jogador PERDEU.\nHistórico: {history_str}\nMissão: Explicar o erro."
        elif status == 'won':
            context = f"{persona} O jogador VENCEU.\nHistórico: {history_str}\nMissão: Parabenizar."
        else:
            context = f"{persona} O jogo está em andamento. Ajude com dúvidas."

        game['chat_history'] = [{"role": "system", "content": context}]