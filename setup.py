import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY=os.getenv("ANTHROPIC_API_KEY")

PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")

CLAUDE_MODEL = "claude-3-7-sonnet-latest"

VECTOR_DB_PATH = "C:/Users/hrm16/OneDrive/Escritorio/chatbot_Cliq/chroma_langchain_db"


