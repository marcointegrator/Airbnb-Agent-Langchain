from pathlib import Path

from dotenv import load_dotenv
from langchain_tavily import TavilySearch
import os

load_dotenv(Path(__file__).parent.parent / ".env")

web_search_tool = TavilySearch(
    max_results=3,
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
    name="web_search_tool",
    description=(
        "Cerca informazioni aggiornate su internet SOLO se rilevanti per l'ospite della casa vacanze. "
        "Usa per: eventi locali, orari farmacie/ospedali, meteo, ristoranti aperti, "
        "trasporti verso Sabaudia, attrazioni turistiche con orari aggiornati. "
        "NON usare per: info sulla casa (usa rag_memory_tool), disponibilità/prezzi, "
        "emergenze (usa escalation_tool), o domande generiche non legate al soggiorno."
    ),
)
