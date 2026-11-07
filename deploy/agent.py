import os
from pathlib import Path
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.models.anthropic import Claude
from agno.vectordb.chroma import ChromaDb
from dotenv import load_dotenv
from agno.os import AgentOS
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent          # pasta deploy/
PDF_PATH = BASE_DIR.parent / "files" / "Panorama_Internacional_Games_2025.pdf"
TMP_DIR = BASE_DIR / "tmp"
TMP_DIR.mkdir(exist_ok=True)                        # cria tmp/ se não existir

# RAG
vector_db = ChromaDb(collection="pdf_agent", path=str(TMP_DIR / "chormadb"),persistent_client=True, embedder=SentenceTransformerEmbedder())
knowledge = Knowledge(vector_db=vector_db)

db = SqliteDb(session_table="agent_session", db_file=str(TMP_DIR / "agent.db"))

db = SqliteDb(session_table="agent_session", db_file="tmp/agent.db")

agent = Agent(
    id="analista_tecnologico",
    name="Ciencia tecnologia",
    model=Claude(id="claude-haiku-5-5", api_key=os.getenv("ANTHROPIC_API_KEY")),
    db=db,
    knowledge=knowledge,
    instructions=["Você é um analista de dados senior que foi encarregado de analisar um pdf com dados tecnologia e ciencia do ano de 2025",
                  "Lembre-se de ser bem criterioso e não deixar passar nenhum detalhe deste assunto, pois é de grande importancia este conteudo",
                  "Gere um relatorio al final da analise com os maiores saltos e maior taxa de melhoria do setor",
    ],
    description="Ciencia tecnologia",
    add_history_to_context=True,
    search_knowledge=True,
    enable_agentic_memory=True,
    num_history_runs=3,
)

# AGENTOS ==================================================================================
agent_os = AgentOS(
    name="Ciencia tecnologia",
    agents=[agent])

app = agent_os.get_app()

# RUN ======================================================================================
if __name__ == "__main__":
    knowledge.insert(
        path=str(PDF_PATH),
        metadata={"source": "Ciencia tecnologia", "type": "pdf", "description": "Panorama Internacional Games 2025"},
        skip_if_exists=True,
        reader=PDFReader(),
    )

    agent_os.serve(app=app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)), reload=False)