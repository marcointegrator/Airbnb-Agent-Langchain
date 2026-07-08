from pathlib import Path

from dotenv import load_dotenv
from langchain.agents.middleware import SummarizationMiddleware
from langchain.chat_models import init_chat_model
import os

load_dotenv(Path(__file__).parent.parent / ".env")

SUMMARY_MODEL = init_chat_model(
    model="claude-haiku-4-5",
    temperature=0,
    api_key=os.getenv("API_KEY"),
    max_tokens=1500,
)

summarization_middleware = SummarizationMiddleware(
    model=SUMMARY_MODEL,
    trigger=("fraction", 0.7),
    keep=("messages", 5),
)
