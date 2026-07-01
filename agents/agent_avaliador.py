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


class AvaliacaoInformatividade(BaseModel):
    classificacao: Literal["high", "medium", "low", "ambiguous"] = Field(
        description="Classificação final da notícia."
    )

    pontuacao: float = Field(
        ge=0,
        le=10,
        description="Pontuação geral de informatividade entre 0 e 10.",
    )

    confianca: float = Field(
        ge=0,
        le=1,
        description="Confiança do modelo na classificação."
    )

    criterios_utilizados: list[str] = Field(
        description="Critérios utilizados na decisão."
    )

    justificativa: str = Field(
        description="Justificativa resumida da classificação."
    )

    necessita_revisao: bool = Field(
        description="Indica se o caso deve ser revisado por um humano."
    )


def consultar_ollama(prompt: str, formato: dict | None = None) -> str:
    url = f"{BASE_URL}/api/generate"

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 700,
        },
    }

    if formato is not None:
        payload["format"] = formato

    try:
        response = requests.post(
            url,
            json=payload,
            headers=HEADERS,
            timeout=90,
        )

        response.raise_for_status()

        return response.json().get("response", "")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar Ollama: {e}")
        return ""


TENTATIVAS = 2


def montar_prompt(
    titulo: str,
    resumo: str,
    atributos: dict,
    contexto: str,
) -> str:

    return f"""
Você é o Agente 3 do pipeline.

Sua função é avaliar a INFORMATIVIDADE de uma notícia.

A classificação NÃO deve refletir sua opinião sobre a notícia.

Ela deve seguir EXCLUSIVAMENTE os critérios apresentados abaixo.

{contexto}

======================================================

NOTÍCIA

Título:
{titulo}

Resumo:
{resumo}

======================================================

ATRIBUTOS EXTRAÍDOS PELO AGENTE 1

{atributos}

======================================================

Analise cuidadosamente.

Considere especialmente:

- especificidade;
- quantidade de informação concreta;
- presença de elementos factuais;
- riqueza do resumo;
- clareza do conteúdo;
- existência de linguagem chamativa.

Retorne APENAS um JSON.

Regras:

classificacao:
- high
- medium
- low
- ambiguous

pontuacao:
valor entre 0 e 10.

confianca:
valor entre 0 e 1.

criterios_utilizados:
lista contendo apenas os critérios realmente utilizados.

justificativa:
explique em poucas linhas.

necessita_revisao:

true quando:

- classificacao = ambiguous

OU

- confianca menor que 0.60

OU

- houver sinais conflitantes.
"""


def validar_saida(avaliacao: AvaliacaoInformatividade):

    revisao = False

    if avaliacao.classificacao == "ambiguous":
        revisao = True

    if avaliacao.confianca < 0.60:
        revisao = True

    if len(avaliacao.justificativa.strip()) < 30:
        revisao = True

    if len(avaliacao.criterios_utilizados) < 2:
        revisao = True

    avaliacao.necessita_revisao = revisao

    return avaliacao


def no_agente_3_avaliador(estado: dict):

    noticia = estado.get("noticia_original", {})

    atributos = estado.get(
        "representacao_estruturado",
        {},
    )

    contexto = estado.get(
        "contexto_formatado",
        "",
    )

    titulo = noticia.get("titulo", "")
    resumo = noticia.get("resumo", "")

    prompt = montar_prompt(
        titulo,
        resumo,
        atributos,
        contexto,
    )

    schema = AvaliacaoInformatividade.model_json_schema()

    for tentativa in range(TENTATIVAS):

        resposta = consultar_ollama(
            prompt,
            formato=schema,
        )

        try:

            avaliacao = (
                AvaliacaoInformatividade.model_validate_json(
                    resposta
                )
            )

            avaliacao = validar_saida(avaliacao)

            return {
                "decisao_final": avaliacao.model_dump()
            }

        except Exception as e:

            print(
                f"Erro na tentativa "
                f"{tentativa + 1}/{TENTATIVAS}"
            )

            print(e)

            print(resposta[:300])

    return {
        "decisao_final": {
            "classificacao": "ambiguous",
            "pontuacao": 5.0,
            "confianca": 0.0,
            "criterios_utilizados": [],
            "justificativa": "Falha na geração da avaliação.",
            "necessita_revisao": True,
        }
    }


if __name__ == "__main__":

    estado = {

        "noticia_original": {

            "titulo": "NASA launches new lunar mission",

            "resumo": (
                "The spacecraft successfully departed "
                "from Cape Canaveral carrying scientific "
                "equipment for future Moon exploration."
            ),

            "categoria": "science",
        },

        "representacao_estruturado": {

            "tema": "Lunar mission",

            "tipo_linguagem": "factual",

            "elementos_factuais": [
                "NASA",
                "Moon",
                "Cape Canaveral",
            ],

            "resumo_acrescenta_info": True,

            "sinais_apelo_superficial": False,
        },

        "contexto_formatado": "Critérios oficiais de informatividade.",
    }

    resultado = no_agente_3_avaliador(estado)

    from pprint import pprint

    pprint(resultado)