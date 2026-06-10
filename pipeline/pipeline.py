import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from estado import EstadoPipeline
from langgraph.graph import END, START, StateGraph

from agents.agent_estruturador import no_agente_1_estruturador

# from agents.agent_recuperador import no_agente_2_recuperador

workflow = StateGraph(EstadoPipeline)

workflow.add_node("Agente_1_Estruturador", no_agente_1_estruturador)
# workflow.add_node("Agente_2_Recuperador", no_agente_2_recuperador)

workflow.add_edge(START, "Agente_1_Estruturador")
# workflow.add_edge("Agente_1_Estruturador", "Agente_2_Recuperador")
# workflow.add_edge("Agente_2_Recuperador", END)

workflow.add_edge("Agente_1_Estruturador", END)

pipeline_compilado = workflow.compile()

ANNOTATION_SOURCES = {
    "pilot": Path(__file__).parent.parent
    / "annotations/manual/mindsmall_train_annotation_pilot_10.csv",
    "main": Path(__file__).parent.parent
    / "annotations/manual/mindsmall_train_annotation_main_40.csv",
    "validation": Path(__file__).parent.parent
    / "annotations/manual/mindsmall_train_annotation_validation_10.csv",
}


def carregar_noticias(fonte: str, limite: int) -> list[dict]:
    path = ANNOTATION_SOURCES[fonte]
    noticias = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            noticias.append(
                {
                    "news_id": row["news_id"],
                    "noticia_original": {
                        "titulo": row["title"],
                        "resumo": row["abstract"],
                        "categoria": row["category"],
                    },
                    "classificacao_manual": row.get("classification", ""),
                }
            )
            if len(noticias) >= limite:
                break
    return noticias


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Testa o pipeline com notícias reais do MIND dataset."
    )
    parser.add_argument(
        "--fonte",
        choices=list(ANNOTATION_SOURCES.keys()),
        default="pilot",
        help="Conjunto de anotações a usar (default: pilot)",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=5,
        help="Número máximo de notícias a processar (default: 5)",
    )
    args = parser.parse_args()

    noticias = carregar_noticias(args.fonte, args.limite)
    print(f"Carregadas {len(noticias)} notícias de '{args.fonte}'.\n")

    for i, item in enumerate(noticias, 1):
        news_id = item["news_id"]
        classificacao_manual = item["classificacao_manual"]
        entrada = {"noticia_original": item["noticia_original"]}

        print(
            f"[{i}/{len(noticias)}] {news_id} | categoria: {item['noticia_original']['categoria']}"
        )
        print(f"  Título: {item['noticia_original']['titulo'][:80]}...")

        resultado = pipeline_compilado.invoke(entrada)
        estruturado = resultado.get("representacao_estruturado", {})
        recuperado = resultado.get("contexto_recuperado", {})
        exemplos = recuperado.get("exemplos", [])

        fatual = estruturado.get("elementos_factuais") or []
        print(
            f"  Agente 1 →  tema: {estruturado.get('tema')}\n"
            f"             linguagem: {estruturado.get('tipo_linguagem')} | "
            f"elementos_factuais: {fatual if fatual else '(nenhum)'}\n"
            f"             resumo acrescenta: {estruturado.get('resumo_acrescenta_info')} | "
            f"apelo superficial: {estruturado.get('sinais_apelo_superficial')}\n"
        )

        print()
