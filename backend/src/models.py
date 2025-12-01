from pydantic import BaseModel, Field
from typing import Optional, List

class StartResponse(BaseModel):
    uuid: str = Field(..., description="Identificador único da sessão do jogo")
    message: str = Field(..., description="Mensagem de boas-vindas")

class QuestionSchema(BaseModel):
    id: int | str
    text: str
    options: List[str]
    prize: float
    currency: str

class AnswerRequest(BaseModel):
    option_index: int = Field(..., ge=0, le=3, description="Índice da opção escolhida (0=A, 1=B, 2=C, 3=D)")

class AnswerResponse(BaseModel):
    result: str = Field(..., description="Mensagem curta de resultado")
    correct: bool = Field(..., description="Booleano indicando se acertou")
    accumulated_prize: str = Field(..., description="Prêmio acumulado formatado")
    explanation: Optional[str] = Field(None, description="Explicação técnica (apenas se acertar)")
    game_status: str = Field(..., description="Estado atual: 'active', 'won', 'lost'")

class ChatCreationResponse(BaseModel):
    message: str
    context_mode: str

class WsInputExample(BaseModel):
    client_message: str = Field(..., description="Mensagem enviada pelo cliente.")

class WsOutputStream(BaseModel):
    response_stream: str = Field(..., description="Pedaço (chunk) de texto gerado pela IA.")

class WsOutputControl(BaseModel):
    type: str = Field("control", description="Tipo da mensagem.")
    content: str = Field("[DONE]", description="Sinal de finalização.")

class WsOutputFull(BaseModel):
    type: str = Field("full_text", description="Tipo da mensagem.")
    content: str = Field(..., description="Texto completo para redundância.")

class WsOutputHistory(BaseModel):
    type: str = Field("history", description="Tipo da mensagem.")
    content: List[dict] = Field(..., description="Histórico completo de mensagens.")

class WsError(BaseModel):
    type: str = Field("error", description="Tipo da mensagem.")
    content: str = Field(..., description="Mensagem de erro.")

class WebSocketProtocolDocs(BaseModel):
    url: str = Field(..., description="URL de conexão.")
    protocol: str = Field("JSON-Only", description="Todas as trocas são objetos JSON.")
    client_sends: WsInputExample
    server_sends_history: WsOutputHistory
    server_sends_stream: WsOutputStream
    server_sends_control: WsOutputControl
    server_sends_redundancy: WsOutputFull
    possible_errors: WsError