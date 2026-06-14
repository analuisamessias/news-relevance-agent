import csv
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

load_dotenv()

API_KEY = os.environ.get("API_KEY", "")
BASE_URL = os.environ.get("BASE_URL")

MODELO_EMBEDDING = "nomic-embed-text"

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
}

RAIZ_PROJETO = Path(__file__).parent.parent
PASTA_CHROMA = RAIZ_PROJETO / "annotations" / "manual"
NOME_COLECAO = "exemplos_anotados"
CSV_EXEMPLOS = PASTA_CHROMA / "mindsmall_train_annotation_main_40.csv"

K_EXEMPLOS = 3

CRITERIOS_OFICIAIS = """\
CRITÉRIOS OFICIAIS DE INFORMATIVIDADE

Níveis de classificação (campo `classification`, valores em inglês):
- high (Alta): informação concreta e específica; o tema/evento principal é
  claro; o resumo acrescenta contexto ou detalhe relevante; não depende de
  apelo superficial para chamar atenção.
- medium (Média): alguma informação relevante e tema central compreensível,
  mas com menor detalhamento, densidade informativa ou especificidade; o
  resumo informa de forma limitada.
- low (Baixa): conteúdo vago, genérico, superficial ou excessivamente
  chamativo; título e resumo acrescentam pouca informação concreta.
- ambiguous (Ambígua): sinais mistos que não permitem classificação segura
  em high, medium ou low; deve ser sinalizada para discussão.

Critérios de apoio:
1. Especificidade: a notícia informa algo concreto (nomes, datas, números,
   locais, instituições) ou permanece vaga?
2. Densidade informativa do resumo: o resumo acrescenta informação relevante
   ao título ou apenas o repete?
3. Clareza do conteúdo principal: após ler título e resumo, fica claro do
   que a notícia trata?
4. Grau de apelo superficial (sinal negativo): o item prioriza chamar
   atenção sem entregar informação correspondente?"""


class EmbeddingsOllamaProxy(Embeddings):

    def embed_query(self, text: str) -> list[float]:
        response = requests.post(
            f"{BASE_URL}/api/embeddings",
            json={"model": MODELO_EMBEDDING, "prompt": text},
            headers=HEADERS,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["embedding"]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]


_vectorstore: Chroma | None = None


def _obter_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name=NOME_COLECAO,
            embedding_function=EmbeddingsOllamaProxy(),
            persist_directory=str(PASTA_CHROMA),
        )
    return _vectorstore


def montar_query(atributos: dict) -> str:
    """Converte os AtributosNoticia do Agente 1 em uma string de busca."""
    elementos = atributos.get("elementos_factuais") or []
    return "\n".join(
        [
            f"Tema: {atributos.get('tema', '')}",
            f"Tipo de linguagem: {atributos.get('tipo_linguagem', '')}",
            "Elementos factuais: " + (", ".join(elementos) if elementos else "nenhum"),
            "Resumo acrescenta informação: "
            + ("sim" if atributos.get("resumo_acrescenta_info") else "não"),
            "Apelo superficial: "
            + ("sim" if atributos.get("sinais_apelo_superficial") else "não"),
        ]
    )


def _formatar_exemplo(indice: int, doc: Document) -> str:
    meta = doc.metadata
    return (
        f"Exemplo {indice} (news_id: {meta.get('news_id', '?')} | "
        f"categoria: {meta.get('category', '?')}"
        f"/{meta.get('subcategory', '?')})\n"
        f"  Título: {meta.get('title', '')}\n"
        f"  Resumo: {meta.get('abstract', '')}\n"
        f"  Classificação: {meta.get('classification', '')} "
        f"(confiança: {meta.get('confidence', '')})\n"
        f"  Justificativa: {meta.get('justification', '')}"
    )


def recuperar_contexto(estado: dict) -> dict:
    """Nó 2 do pipeline: recupera critérios + exemplos similares via RAG.

    Lê `representacao_estruturado` do estado, busca os K_EXEMPLOS exemplos
    anotados mais similares no ChromaDB e devolve:
    - `contexto_recuperado`: dict com a query usada e os exemplos brutos;
    - `contexto_formatado`: string final (critérios + exemplos) para o
      Agente 3.
    """
    atributos = estado.get("representacao_estruturado", {})
    query = montar_query(atributos)

    try:
        documentos = _obter_vectorstore().similarity_search(query, k=K_EXEMPLOS)
    except Exception as e:
        print(f"Erro na busca vetorial do Agente 2: {e}")
        documentos = []

    exemplos = [doc.metadata for doc in documentos]

    if documentos:
        bloco_exemplos = "\n\n".join(
            _formatar_exemplo(i, doc) for i, doc in enumerate(documentos, 1)
        )
        bloco_exemplos = (
            "EXEMPLOS ANOTADOS MANUALMENTE MAIS SIMILARES À NOTÍCIA ATUAL\n\n"
            + bloco_exemplos
        )
    else:
        bloco_exemplos = "(Nenhum exemplo recuperado do banco vetorial.)"

    contexto_formatado = f"{CRITERIOS_OFICIAIS}\n\n{bloco_exemplos}"

    return {
        "contexto_recuperado": {"query": query, "exemplos": exemplos},
        "contexto_formatado": contexto_formatado,
    }


no_agente_2_recuperador = recuperar_contexto


# ---------------------------------------------------------------------------
# Ingestão: popula o ChromaDB a partir das anotações manuais (rodar uma vez)
# ---------------------------------------------------------------------------


def inicializar_banco(csv_path: Path = CSV_EXEMPLOS) -> int:
    """Indexa as anotações manuais no ChromaDB, se a coleção estiver vazia.

    O conteúdo embutido é título + resumo (o que melhor representa a notícia
    para busca por similaridade); os demais campos viram metadados.
    Retorna o número de documentos na coleção ao final.
    """
    vectorstore = _obter_vectorstore()
    existentes = vectorstore._collection.count()
    if existentes > 0:
        print(f"Coleção '{NOME_COLECAO}' já possui {existentes} documentos.")
        return existentes

    documentos = []
    ids = []
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            documentos.append(
                Document(
                    page_content=(
                        f"Título: {row['title']}\n"
                        f"Resumo: {row['abstract']}\n"
                        f"Categoria: {row['category']}/{row['subcategory']}"
                    ),
                    metadata={campo: row.get(campo, "") for campo in row},
                )
            )
            ids.append(row["news_id"])

    vectorstore.add_documents(documentos, ids=ids)
    total = vectorstore._collection.count()
    print(f"Indexados {total} exemplos de '{csv_path.name}' " f"em '{PASTA_CHROMA}'.")
    return total


if __name__ == "__main__":
    inicializar_banco()
