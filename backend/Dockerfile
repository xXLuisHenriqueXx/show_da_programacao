# Usa uma imagem oficial leve do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Variáveis de ambiente para otimizar o Python no Docker
# PYTHONDONTWRITEBYTECODE: Impede que o Python grave arquivos .pyc
# PYTHONUNBUFFERED: Garante que os logs sejam enviados diretamente para o terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copia e instala as dependências primeiro (aproveita o cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte para dentro da pasta /app/src
COPY src/ ./src/

# Expõe a porta padrão do FastAPI/Uvicorn
EXPOSE 8000

# Cria um usuário não-root para segurança (opcional, mas recomendado para produção)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Comando de execução
# Ajuste 'src.main:app' se o nome do seu arquivo ou instância mudar
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]