from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Descrição detalhada do erro ocorrido.")

class StartResponse(BaseModel):
    uuid: str = Field(..., description="Identificador único da sessão do jogo. Use este UUID em todas as requisições subsequentes.")
    message: str = Field(..., description="Mensagem de boas-vindas configurada no servidor.")

class ResetResponse(BaseModel):
    message: str = Field(..., description="Mensagem de confirmação.")
    current_question_id: int | str = Field(..., description="ID da primeira pergunta do nível reiniciado.")

class QuestionSchema(BaseModel):
    id: int | str = Field(..., description="ID da pergunta (numérico para estáticas, string para geradas).")
    text: str = Field(..., description="O enunciado da pergunta.")
    options: List[str] = Field(..., description="Lista de 4 alternativas de resposta.")
    prize: float = Field(..., description="Valor do prêmio para esta pergunta específica.")
    currency: str = Field(..., description="Símbolo da moeda (ex: R$).")

class GameWonSchema(BaseModel):
    status: str = Field("WIN", description="Sinalizador de vitória.")
    message: str = Field(..., description="Mensagem instruindo o jogador a avançar de nível.")

class NextLevelAccepted(BaseModel):
    message: str = Field(..., description="Confirmação de que a geração iniciou.")

class GenerationStatusResponse(BaseModel):
    status: str = Field(..., description="Estados possíveis: 'idle' (parado), 'generating' (processando), 'completed' (sucesso), 'error' (falha).")
    message: str = Field(..., description="Mensagem amigável de status.")

class AnswerRequest(BaseModel):
    option_index: int = Field(..., ge=0, le=3, description="Índice da opção escolhida (0=A, 1=B, 2=C, 3=D).")

class AnswerResponse(BaseModel):
    result: str = Field(..., description="Mensagem curta de feedback (Correto/Errado).")
    correct: bool = Field(..., description="Booleano indicando se a resposta foi aceita.")
    accumulated_prize: str = Field(..., description="Prêmio acumulado formatado com a moeda.")
    explanation: Optional[str] = Field(None, description="Explicação técnica da resposta (retornado mesmo se errar, para aprendizado).")
    game_status: str = Field(..., description="Estado atual do jogo: 'active' (continua), 'won' (venceu bloco), 'lost' (fim de jogo).")

class ChatCreationResponse(BaseModel):
    message: str = Field(..., description="Confirmação de inicialização.")
    context_mode: str = Field(..., description="Indica qual contexto foi carregado no tutor (ex: 'active', 'won', 'lost').")

class WsInputExample(BaseModel):
    client_message: str = Field(..., description="Mensagem de texto enviada pelo usuário.")

class WsOutputStream(BaseModel):
    response_stream: str = Field(..., description="Fragmento de texto (token) da resposta da IA.")

class WsOutputControl(BaseModel):
    type: str = Field("control", description="Identificador fixo.")
    content: str = Field("[DONE]", description="Sinaliza que o stream de resposta acabou.")

class WsOutputFull(BaseModel):
    type: str = Field("full_text", description="Identificador fixo.")
    content: str = Field(..., description="Texto completo da resposta para garantir integridade e redundância.")

class WsOutputHistory(BaseModel):
    type: str = Field("history", description="Identificador fixo.")
    content: List[Dict[str, Any]] = Field(..., description="Lista de mensagens anteriores para reconstruir o chat no frontend.")

class WsError(BaseModel):
    type: str = Field("error", description="Identificador fixo.")
    content: str = Field(..., description="Descrição do erro ocorrido no socket.")

class WebSocketProtocolDocs(BaseModel):
    url: str = Field(..., description="URL completa para conexão WebSocket.")
    protocol: str = Field("JSON-Only", description="Protocolo estrito: todas as mensagens são objetos JSON serializados.")
    client_sends: WsInputExample
    server_sends_history: WsOutputHistory
    server_sends_stream: WsOutputStream
    server_sends_control: WsOutputControl
    server_sends_redundancy: WsOutputFull
    possible_errors: WsError