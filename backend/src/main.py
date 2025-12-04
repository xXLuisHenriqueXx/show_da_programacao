import json
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.services.game_manager import GameManager
from src.services.openai_service import OpenAIClient
from src.models import (
    StartResponse, AnswerRequest, AnswerResponse, 
    QuestionSchema, WebSocketProtocolDocs, 
    GameWonSchema, GenerationStatusResponse, NextLevelAccepted,
    ErrorResponse, ResetResponse
)

tags_metadata = [
    {"name": "Game Flow", "description": "Gerenciamento de sessão, perguntas e respostas."},
    {"name": "Tutor AI", "description": "Interação em tempo real com o assistente inteligente."},
]

app = FastAPI(
    title="Jogo do Milhão AI", 
    version="2.11.0", 
    description="API para Quiz Game com suporte a IA Generativa e Tutoria em Tempo Real.",
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_manager = GameManager()
ai_client = OpenAIClient()

@app.post(
    "/start", 
    response_model=StartResponse, 
    tags=["Game Flow"],
    summary="Inicia uma nova sessão",
    description="Cria uma nova instância de jogo, gera um UUID único e reinicia o estado do jogador."
)
async def start_game():
    uuid = game_manager.create_game()
    welcome = game_manager.settings.get("welcome_message", "Jogo iniciado.")
    return {"uuid": uuid, "message": welcome}

@app.post(
    "/reset/{uuid}",
    response_model=ResetResponse,
    responses={
        200: {"description": "Nível reiniciado com sucesso.", "model": ResetResponse},
        404: {"description": "Jogo não encontrado.", "model": ErrorResponse}
    },
    tags=["Game Flow"],
    summary="Reinicia o nível atual",
    description="Reseta o progresso do jogador (índice e prêmio) mas MANTÉM as perguntas atuais."
)
async def reset_game(uuid: str):
    success = game_manager.reset_game(uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    
    current_q = game_manager.get_current_question(uuid)
    return {
        "message": "Nível reiniciado. Boa sorte desta vez!",
        "current_question_id": current_q['id']
    }

@app.get(
    "/question/{uuid}",
    response_model=QuestionSchema,                 
    responses={
        200: {"description": "Pergunta retornada com sucesso.", "model": QuestionSchema},
        201: {"description": "Nível concluído (Vitória).", "model": GameWonSchema},
        404: {"description": "Jogo não encontrado ou expirado.", "model": ErrorResponse},
    },
    tags=["Game Flow"],
    summary="Obtém a pergunta atual"
)
async def get_next_question(uuid: str):
    result = game_manager.get_current_question(uuid)
    
    if result is None: 
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    
    if result == "WIN": 
        return JSONResponse(
            status_code=201, 
            content={"status": "WIN", "message": "Você venceu! Use /next-level."}
        )
    return result

@app.post(
    "/answer/{uuid}", 
    response_model=AnswerResponse, 
    responses={
        200: {"description": "Resposta Correta.", "model": AnswerResponse},
        406: {"description": "Resposta Errada (Game Over).", "model": AnswerResponse},
        404: {"description": "Jogo não encontrado.", "model": ErrorResponse}
    },
    tags=["Game Flow"],
    summary="Envia uma resposta"
)
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
    
    return JSONResponse(status_code=200, content=response_data)

@app.post(
    "/next-level/{uuid}", 
    status_code=202, 
    response_model=NextLevelAccepted,
    responses={
        202: {"description": "Geração iniciada em background.", "model": NextLevelAccepted},
        400: {"description": "Não permitido.", "model": ErrorResponse},
        404: {"description": "Jogo não encontrado.", "model": ErrorResponse}
    },
    tags=["Game Flow"],
    summary="Solicita geração de novas perguntas"
)
async def generate_next_level(uuid: str, background_tasks: BackgroundTasks):
    game = game_manager.get_game(uuid)
    if not game: raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    
    if game['status'] != 'won':
        raise HTTPException(status_code=400, detail="Vença o nível atual primeiro.")
    
    game_manager.set_generation_status(uuid, "generating")
    background_tasks.add_task(game_manager.background_generate_level, uuid, ai_client)
    
    return {"message": "Geração iniciada. Verifique o status."}

@app.get(
    "/next-level/{uuid}/status", 
    response_model=GenerationStatusResponse, 
    tags=["Game Flow"],
    summary="Verifica status da geração"
)
async def check_generation_status(uuid: str):
    status_data = game_manager.get_generation_status(uuid)
    return status_data

@app.get(
    "/ws/chat/{uuid}/docs", 
    response_model=WebSocketProtocolDocs, 
    tags=["Tutor AI"],
    summary="Documentação do Protocolo WebSocket"
)
async def get_websocket_protocol(uuid: str):
    return {
        "url": f"ws://SEU_HOST:8000/ws/chat/{uuid}",
    }

@app.websocket("/ws/chat/{uuid}")
async def websocket_endpoint(websocket: WebSocket, uuid: str):
    await websocket.accept()
    game = game_manager.get_game(uuid)
    
    if not game:
        await websocket.close(code=4000)
        return

    game_manager.init_tutor_context(uuid)

    visible_history = [msg for msg in game['chat_history'] if msg['role'] != 'system']
    await websocket.send_text(json.dumps({
        "type": "history",
        "content": visible_history
    }))

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
            
            async for chunk in ai_client.get_streaming_response(
                messages=game['chat_history'], 
                vector_store_id=vector_id
            ):
                full_response += chunk
                await websocket.send_text(json.dumps({"response_stream": chunk})) 
            
            await websocket.send_text(json.dumps({"type": "control", "content": "[DONE]"}))
            await websocket.send_text(json.dumps({
                "type": "full_text", 
                "content": full_response
            }))
            
            game['chat_history'].append({"role": "assistant", "content": full_response})
            
    except WebSocketDisconnect:
        print(f"Chat finalizado para {uuid}")