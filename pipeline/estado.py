from typing import TypedDict


class EstadoPipeline(TypedDict):
    noticia_original: dict

    representacao_estruturado: dict

    contexto_recuperado: dict
    contexto_formatado: str

    decisao_final: dict

    verificacao: dict

    comparacao: dict
