import json
import os
import re
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
        description="Tema principal da notícia em até 10 palavras, em português."
    )
    tipo_linguagem: Literal["factual", "chamativo", "misto"] = Field(
        description=(
            "'factual': tom neutro e informativo. "
            "'chamativo': linguagem sensacionalista ou de apelo. "
            "'misto': combina os dois."
        )
    )
    elementos_factuais: list[str] = Field(
        description="Lista de elementos concretos (nomes, datas, números, locais, instituições). Vazio se não houver."
    )
    resumo_acrescenta_info: bool = Field(
        description="true se o resumo acrescenta contexto além do título. false se apenas repete."
    )
    sinais_apelo_superficial: bool = Field(
        description="true se o item prioriza apelo sensacionalista sem informação correspondente."
    )


def consultar_ollama(prompt: str) -> str:
    url = f"{BASE_URL}/api/generate"

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 512},
    }

    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao comunicar com Ollama: {e}")
        return ""


def no_agente_1_estruturador(estado: dict) -> dict:
    noticia = estado.get("noticia_original", {})
    titulo = noticia.get("titulo", "")
    resumo = noticia.get("resumo", "")
    categoria_original = noticia.get("categoria", "")

    prompt = f"""Você é um analista preparando notícias para classificação de informatividade.
Informatividade é o grau em que uma notícia apresenta informação concreta e específica,
em vez de conteúdo vago, genérico ou predominantemente chamativo.
Responda sempre em português. Não deixe de preencher nenhum campo.

Analise a notícia abaixo e retorne APENAS o JSON preenchido (sem markdown, sem texto adicional).

Título: {titulo}
Resumo: {resumo}
Categoria: {categoria_original}

Perguntas orientadoras:
1. Quais elementos concretos aparecem? (nomes de pessoas, locais, instituições, números, datas)
2. O resumo acrescenta algo além do que o título já diz?
3. O item parece priorizar sensacionalismo/apelo em vez de informação?

Exemplo de resposta para uma notícia sobre investimento da Microsoft em IA:
{{
  "tema": "investimento em IA",
  "tipo_linguagem": "factual",
  "elementos_factuais": ["Microsoft", "OpenAI", "US$ 10 bilhões", "2023"],
  "resumo_acrescenta_info": true,
  "sinais_apelo_superficial": false
}}

Restrições:
- "tema": máximo 10 palavras em português, NÃO copie o título
- "tipo_linguagem": exatamente "factual", "chamativo" ou "misto"
- "elementos_factuais": lista de strings — vazia ([]) se não houver elementos concretos
- campos booleanos: exatamente true ou false (sem aspas)

Resposta JSON:"""

    resposta_texto = consultar_ollama(prompt)

    try:
        match = re.search(r"\{.*\}", resposta_texto, re.DOTALL)
        if not match:
            raise ValueError("Nenhum JSON encontrado na resposta")

        resultado = json.loads(match.group())

        atributos = AtributosNoticia(**resultado)
        return {"representacao_estruturado": atributos.model_dump()}
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Erro ao processar resposta do Ollama: {e}")
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
