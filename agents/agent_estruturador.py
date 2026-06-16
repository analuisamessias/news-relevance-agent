import os
from typing import Literal

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

API_KEY = os.environ.get("API_KEY", "")
BASE_URL = os.environ.get("BASE_URL")

MODELO = "llama3.2:3b"

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
}


class AtributosNoticia(BaseModel):
    tema: str = Field(
        description=("Tema principal da notícia em até 10 palavras, em português.")
    )
    tipo_linguagem: Literal["factual", "chamativo", "misto"] = Field(
        description=(
            "'factual': tom neutro e informativo. "
            "'chamativo': linguagem sensacionalista ou de apelo. "
            "'misto': combina os dois."
        )
    )
    elementos_factuais: list[str] = Field(
        description=(
            "Lista de elementos concretos (nomes, datas, números, "
            "locais, instituições). Vazio se não houver."
        )
    )
    resumo_acrescenta_info: bool = Field(
        description=(
            "true se o resumo acrescenta contexto além do título. "
            "false se apenas repete."
        )
    )
    sinais_apelo_superficial: bool = Field(
        description=(
            "true se o item prioriza apelo sensacionalista sem "
            "informação correspondente."
        )
    )


def consultar_ollama(prompt: str, formato: dict | None = None) -> str:
    url = f"{BASE_URL}/api/generate"

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 512},
    }

    if formato is not None:
        payload["format"] = formato

    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao comunicar com Ollama: {e}")
        return ""


TENTATIVAS = 2


def no_agente_1_estruturador(estado: dict) -> dict:
    noticia = estado.get("noticia_original", {})
    titulo = noticia.get("titulo", "")
    resumo = noticia.get("resumo", "")
    categoria_original = noticia.get("categoria", "")

    prompt = f"""\
Você é um analista preparando notícias para classificação de
informatividade. Informatividade é o grau em que uma notícia
apresenta informação concreta e específica, em vez de conteúdo
vago, genérico ou predominantemente chamativo.

Analise APENAS a notícia abaixo. Baseie cada campo somente no que está
escrito no título e no resumo; não invente informações externas.

Título: {titulo}
Resumo: {resumo}
Categoria: {categoria_original}

Preencha os campos do JSON assim:
- "tema": tema principal DESTA notícia, em inglês, com no máximo 10
  palavras. Descreva o assunto com suas palavras; não copie o título.
- "tipo_linguagem": "factual" se o tom é neutro e informativo; "chamativo"
  se é sensacionalista ou de apelo; "misto" se combina os dois.
- "elementos_factuais": lista apenas com elementos concretos que aparecem
  no título ou no resumo (nomes de pessoas, locais, instituições, números,
  datas). Lista vazia se não houver.
- "resumo_acrescenta_info": compare o resumo com o título. true se o resumo
  traz QUALQUER detalhe novo que o título não menciona (local, data, hora,
  números, circunstâncias, explicações); false somente se o resumo apenas
  repete o título, está vazio ou não informa nada novo.
- "sinais_apelo_superficial": true se o item prioriza chamar atenção de
  forma vaga ou sensacionalista, sem entregar informação correspondente."""

    schema = AtributosNoticia.model_json_schema()

    for tentativa in range(1, TENTATIVAS + 1):
        resposta_texto = consultar_ollama(prompt, formato=schema)

        try:
            atributos = AtributosNoticia.model_validate_json(resposta_texto)
            return {"representacao_estruturado": atributos.model_dump()}
        except ValueError as e:
            print(f"Tentativa {tentativa}/{TENTATIVAS} do Agente 1 falhou: {e}")
            print(f"Resposta recebida: {resposta_texto[:200]}")

    return {
        "representacao_estruturado": {
            "tema": "Desconhecido",
            "tipo_linguagem": "misto",
            "elementos_factuais": [],
            "resumo_acrescenta_info": False,
            "sinais_apelo_superficial": False,
        }
    }
