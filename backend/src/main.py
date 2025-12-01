import json
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from src.services.game_manager import GameManager
from src.services.openai_service import OpenAIClient
from src.models import (
    StartResponse, AnswerRequest, AnswerResponse, 
    ChatCreationResponse, QuestionSchema, WebSocketProtocolDocs
)

tags_metadata = [
    {"name": "Game Flow", "description": "Controle do jogo e fluxo de perguntas."},
    {"name": "Tutor AI", "description": "Chat WebSocket e Geração de Conteúdo."},
]

app = FastAPI(title="Jogo do Milhão AI", version="2.6.0", openapi_tags=tags_metadata)

game_manager = GameManager()
ai_client = OpenAIClient()

@app.post("/start", response_model=StartResponse, tags=["Game Flow"])
async def start_game():
    uuid = game_manager.create_game()
    welcome = game_manager.settings.get("welcome_message", "Jogo iniciado.")
    return {"uuid": uuid, "message": welcome}

@app.get("/question/{uuid}", response_model=QuestionSchema | dict, tags=["Game Flow"])
async def get_next_question(uuid: str):
    result = game_manager.get_current_question(uuid)
    if result is None: raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    if result == "WIN": return {"status": "WIN", "message": "Você venceu! Use /next-level."}
    return result

@app.post("/answer/{uuid}", response_model=AnswerResponse, tags=["Game Flow"])
async def answer_question(uuid: str, payload: AnswerRequest):
    game = game_manager.get_game(uuid)
    if not game: raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    
    current_list = game_manager.static_questions if game['mode'] == 'static' else game['generated_questions']
    idx = game['current_question_index']
    explanation = current_list[idx].get('explanation', '') if idx < len(current_list) else ""

    is_correct = game_manager.submit_answer(uuid, payload.option_index)
    currency = game_manager.settings.get("currency_symbol", "$")

    response_data = {
        "result": "Correto!" if is_correct else "Errado!",
        "correct": is_correct,
        "accumulated_prize": f"{currency} {game['accumulated_prize']}",
        "explanation": explanation,
        "game_status": game['status']
    }
    return JSONResponse(status_code=200 if is_correct else 406, content=response_data)

@app.post("/next-level/{uuid}", tags=["Game Flow"])
async def generate_next_level(uuid: str):
    game = game_manager.get_game(uuid)
    if not game or game['status'] != 'won':
        raise HTTPException(status_code=400, detail="Vença o nível atual primeiro.")
    
    success = game_manager.generate_next_level(uuid, ai_client)
    
    if not success: raise HTTPException(status_code=500, detail="Erro na IA.")
    return {"message": "Novo nível gerado!"}

@app.post("/chat/{uuid}/prepare", response_model=ChatCreationResponse, tags=["Tutor AI"])
async def prepare_tutor(uuid: str):
    game = game_manager.get_game(uuid)
    if not game: raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    game_manager.init_tutor_context(uuid)
    return {"message": "Tutor pronto.", "context_mode": game['status']}

@app.get("/ws/chat/{uuid}/docs", response_model=WebSocketProtocolDocs, tags=["Tutor AI"])
async def get_websocket_protocol(uuid: str):
    return {
        "url": f"ws://SEU_HOST:8000/ws/chat/{uuid}",
        "protocol": "JSON-Only",
        "client_sends": {"client_message": "Texto do usuário"},
        "server_sends_history": {
            "type": "history", 
            "content": [{"role": "user", "content": "..."}]
        },
        "server_sends_stream": {"response_stream": "chunk"},
        "server_sends_control": {"type": "control", "content": "[DONE]"},
        "server_sends_redundancy": {
            "type": "full_text", 
            "content": "Texto completo..."
        },
        "possible_errors": {"type": "error", "content": "Erro..."}
    }

@app.websocket("/ws/chat/{uuid}")
async def websocket_endpoint(websocket: WebSocket, uuid: str):
    await websocket.accept()
    game = game_manager.get_game(uuid)
    
    if not game:
        await websocket.close(code=4000)
        return

    if not game.get('chat_history'):
        error_payload = json.dumps({"type": "error", "content": "Chame POST /prepare antes."})
        await websocket.send_text(error_payload)
        await websocket.close(code=4003)
        return

    visible_history = [msg for msg in game['chat_history'] if msg['role'] != 'system']
    
    history_payload = json.dumps({
        "type": "history",
        "content": visible_history
    })
    await websocket.send_text(history_payload)

    vector_id = game_manager.vector_store_id

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
                user_msg = data.get("client_message")
                if not user_msg: continue
            except json.JSONDecodeError:
                continue

            game['chat_history'].append({"role": "user", "content": user_msg})
            
            full_response = ""
            
            for chunk in ai_client.get_streaming_response(
                messages=game['chat_history'], 
                vector_store_id=vector_id
            ):
                full_response += chunk
                response_payload = json.dumps({"response_stream": chunk})
                await websocket.send_text(response_payload) 
            
            control_payload = json.dumps({"type": "control", "content": "[DONE]"})
            await websocket.send_text(control_payload)
            
            final_message_payload = json.dumps({
                "type": "full_text", 
                "content": full_response
            })
            await websocket.send_text(final_message_payload)
            
            game['chat_history'].append({"role": "assistant", "content": full_response})
            
    except WebSocketDisconnect:
        print(f"Chat finalizado para {uuid}")