# AIRBNB (LangChain Agent)

Questa cartella contiene un agente LangChain che fa da assistente per gli ospiti della casa vacanze **"L'Oasi di Sabaudia"**.
L’agente risponde in modo cordiale e multilingua, usando:

- una **knowledge base locale (RAG)** per domande su casa/servizi/regole/zona
- una **web search** solo quando serve informazione realmente aggiornata
- un tool di **escalation via Telegram** per emergenze o richieste non gestibili
- tool **MCP Hospitable** per calendario, disponibilità e messaggistica delle prenotazioni

## Struttura

- `agent.py`: orchestration dell’agente (prompt di sistema + tool)
- `data/`: documenti (es. `casa_info.md`) usati per alimentare la knowledge base
- `tools/`:
  - `ingest_knowledge.py`: ingest dei file di `data/` -> Chroma
  - `rag_memory_tool.py`: tool RAG (ricerca nella knowledge base)
  - `web_search_tool.py`: tool di ricerca internet (Tavily)
  - `escalation_tool.py`: invio messaggi al proprietario su Telegram
  - `hospitable.py`: caricamento tool MCP Hospitable (con allowlist)
  - `summarizer_tool.py`: middleware per riassumere conversazioni lunghe
  - `clear_chroma_db.py`: reset della knowledge base locale (Chroma)
- `.env`: variabili d’ambiente con chiavi/tokens (non committare)

## Flusso di esecuzione

1. **Popola la knowledge base locale (Chroma)**

   ```bash
   python -m tools.ingest_knowledge
   ```

   Legge tutti i file in `data/` con estensione `.md` o `.txt`, li spezza in chunk e li salva in una collection Chroma.

2. **Avvia l’agente**

   ```bash
   python agent.py
   ```

   Scrivi la richiesta quando richiesto (`quit` per uscire).

3. **(Opzionale) Reset knowledge base**

   ```bash
   python -m tools.clear_chroma_db
   ```

## Tool disponibili (in pratica)

- **RAG: `rag_memory_tool`**
  - cerca nella knowledge base tramite similarity search su Chroma
  - usa embeddings OpenAI (`text-embedding-3-large`)
  - è pensato per essere usato “prima” su domande su casa/zona/regole/servizi

- **Web: `web_search_tool`**
  - usa Tavily per informazioni aggiornate (eventi, meteo, orari, ristoranti aperti, ecc.)
  - non deve essere usato per info sulla casa: per quello usa il RAG

- **Escalation: `escalation_tool`**
  - invia una notifica al proprietario via Telegram quando serve assistenza/emergenze

- **MCP Hospitable (in `tools/hospitable.py`)**
  - carica tool da `https://mcp.hospitable.com/mcp` tramite token
  - include funzioni per:
    - calendario e disponibilità
    - ricerca proprietà
    - creazione preventivi
    - liste/dettagli prenotazioni e messaggi
    - invio messaggi sul thread (quando l’agente è pronto a contattare davvero l’ospite)

## Variabili d'ambiente (`.env`)

L’agente e i tool leggono `.env`. In particolare:

- `API_KEY` (Claude: `init_chat_model` e riassunto)
- `OPENAI_API_KEY` (embeddings per la knowledge base)
- `TAVILY_API_KEY` (web search)
- `TELEGRAM_BOT_TOKEN` e `TELEGRAM_OWNER_CHAT_ID` (escalation su Telegram)
- `HOSPITABLE_MCP_TOKEN` (accesso ai tool MCP Hospitable)

## Note sulla sicurezza

Il file `.env` contiene segreti/tokens. Deve restare **ignorato da git** e non va mai pubblicato.

