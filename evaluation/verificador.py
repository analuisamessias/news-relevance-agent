from typing import Any


LIMIAR_CONFIANCA = 0.60


def verificar_avaliacao(avaliacao: dict[str, Any]) -> dict[str, Any]:
    """
    Verifica a consistência da avaliação produzida pelo Agente 3.

    Retorna:
        {
            "valida": bool,
            "necessita_revisao": bool,
            "problemas": [...]
        }
    """

    problemas = []

    classificacao = avaliacao.get("classificacao")
    pontuacao = avaliacao.get("pontuacao", 0)
    confianca = avaliacao.get("confianca", 0)
    justificativa = avaliacao.get("justificativa", "")
    criterios = avaliacao.get("criterios_utilizados", [])

    if classificacao not in {
        "high",
        "medium",
        "low",
        "ambiguous",
    }:
        problemas.append("Classificação inválida.")

    if not (0 <= pontuacao <= 10):
        problemas.append("Pontuação fora da faixa permitida.")

    if not (0 <= confianca <= 1):
        problemas.append("Confiança inválida.")

    if len(justificativa.strip()) < 30:
        problemas.append("Justificativa muito curta.")

    if len(criterios) < 2:
        problemas.append("Poucos critérios utilizados.")

    if confianca < LIMIAR_CONFIANCA:
        problemas.append("Baixa confiança.")

    if classificacao == "ambiguous":
        problemas.append("Classificação ambígua.")

    necessita_revisao = len(problemas) > 0

    return {
        "valida": len(problemas) == 0,
        "necessita_revisao": necessita_revisao,
        "problemas": problemas,
    }