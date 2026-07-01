from typing import Any


def comparar_com_anotacao(
    avaliacao_agente: dict[str, Any],
    classificacao_manual: str,
) -> dict[str, Any]:
    """
    Compara a classificação do agente com a classificação manual.
    """

    prevista = avaliacao_agente.get("classificacao", "").lower().strip()
    real = classificacao_manual.lower().strip()

    correto = prevista == real

    return {
        "classificacao_prevista": prevista,
        "classificacao_real": real,
        "correto": correto,
    }


def comparar_varias(predicoes: list[dict]) -> list[dict]:
    """
    Apenas organiza os resultados de comparação.
    """

    resultados = []

    for item in predicoes:

        resultados.append(
            comparar_com_anotacao(
                item["avaliacao"],
                item["manual"],
            )
        )

    return resultados