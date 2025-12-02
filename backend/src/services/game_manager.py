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
            "generation_status": "idle", 
            "generated_questions": [],
            "history": [],
            "chat_history": [] 
        }
        return game_id

    def get_game(self, game_id: str) -> Optional[dict]:
        return self.games.get(game_id)

    def reset_game(self, game_id: str) -> bool:
        """Reinicia o nível atual mantendo as perguntas mas zerando o progresso."""
        game = self.get_game(game_id)
        if not game: return False

        # Reinicia estado do jogo
        game['current_question_index'] = 0
        game['accumulated_prize'] = 0
        game['status'] = 'active'
        game['history'] = [] # Limpa histórico de acertos/erros desta rodada
        
        # Reinicia o tutor e avisa sobre o reset
        self.init_tutor_context(game_id)
        
        # Adiciona contexto extra para o tutor saber que é uma nova tentativa
        retry_context = "SISTEMA: O jogador optou por REINICIAR (Reset) este nível. Ele está tentando novamente as mesmas perguntas. Seja encorajador e considere que ele pode já ter visto essas questões antes."
        game['chat_history'].append({"role": "system", "content": retry_context})
        
        return True

    def get_generation_status(self, game_id: str) -> dict:
        game = self.get_game(game_id)
        if not game:
            return {"status": "error", "message": "Jogo não encontrado"}
        return {
            "status": game.get("generation_status", "idle"),
            "message": "Aguardando..." if game.get("generation_status") == "generating" else "Concluído"
        }

    def set_generation_status(self, game_id: str, status: str):
        game = self.get_game(game_id)
        if game:
            game["generation_status"] = status

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

    def background_generate_level(self, game_id: str, ai_client: LLMClientInterface):
        """Executada em background task com retries, validação e quantidade dinâmica."""
        game = self.get_game(game_id)
        if not game: return

        qty_questions = self.settings.get("generated_questions_quantity", 4) 

        history_str = json.dumps(game.get('history', []), ensure_ascii=False)
        chat_context = [
            {"role": m["role"], "content": m["content"]} 
            for m in game.get('chat_history', []) 
            if m.get('role') != 'system'
        ]
        chat_str = json.dumps(chat_context, ensure_ascii=False)

        base_instruction = self.settings.get('tutor_question_generations_instructions', "")
        system_prompt = (
            f"{base_instruction}\n\n"
            "ATUAÇÃO: Você é um Motor de Geração de Conteúdo Adaptativo para ensino de programação.\n"
            f"TAREFA: Gere um novo nível contendo EXATAMENTE {qty_questions} perguntas de múltipla escolha.\n\n"
            "CONTEXTO DO JOGADOR:\n"
            f"- Histórico de Jogo: {history_str}\n"
            f"- Conversas com Tutor: {chat_str}\n\n"
            "DIRETRIZES:\n"
            "1. Baseie-se nas dúvidas expressas no chat.\n"
            "2. Se houve erros, reforce os conceitos.\n"
            "3. Se houve acertos fáceis, aumente a dificuldade.\n"
            "4. Retorne APENAS JSON válido.\n\n"
            "FORMATO JSON OBRIGATÓRIO:\n"
            "{\n"
            "  \"questions\": [\n"
            "    {\n"
            "      \"id\": \"gen_<uuid>\",\n"
            "      \"text\": \"...\",\n"
            "      \"options\": [\"A\", \"B\", \"C\", \"D\"],\n"
            "      \"correct_option\": \"...\",\n"
            "      \"explanation\": \"...\",\n"
            "      \"prize\": 10000\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                json_str = ai_client.generate_structured_content(
                    system_prompt=system_prompt,
                    user_prompt=f"Gere o próximo nível com {qty_questions} questões (Tentativa {attempt+1}).",
                    vector_store_id=self.vector_store_id
                )

                clean_json = json_str.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)

                if "questions" not in data or not isinstance(data["questions"], list):
                    raise ValueError("JSON inválido: chave 'questions' ausente ou mal formatada.")
                
                if len(data["questions"]) != qty_questions:
                    raise ValueError(f"Quantidade incorreta: esperava {qty_questions}, recebeu {len(data['questions'])}")

                first_q = data["questions"][0]
                required_keys = ["text", "options", "correct_option", "explanation", "prize"]
                if not all(k in first_q for k in required_keys):
                     raise ValueError("JSON inválido: campos obrigatórios da pergunta ausentes.")

                game['generated_questions'] = data['questions']
                game['mode'] = 'generated'
                game['current_question_index'] = 0
                game['status'] = 'active'
                game['generation_status'] = 'completed'
                return 

            except (json.JSONDecodeError, ValueError, Exception) as e:
                print(f"Tentativa {attempt+1} falhou: {e}")
                if attempt == max_retries - 1:
                    game['generation_status'] = 'error'

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
            context = (
                f"{persona} O jogo está em andamento.\n"
                f"Histórico de jogadas até agora: {history_str}\n"
                "Missão: Ajude com dúvidas sobre a pergunta atual ou as anteriores."
            )

        game['chat_history'] = [{"role": "system", "content": context}]