import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from estado import EstadoPipeline
from langgraph.graph import END, START, StateGraph

from agents.agent_estruturador import no_agente_1_estruturador
from agents.agent_recuperador import no_agente_2_recuperador

from agents.agent_avaliador import no_agente_3_avaliador

from evaluation.verificador import verificar_avaliacao
from evaluation.comparador import comparar_com_anotacao

workflow = StateGraph(EstadoPipeline)

def no_verificador(estado: dict):

    verificacao = verificar_avaliacao(
        estado["decisao_final"]
    )

    return {
        "verificacao": verificacao
    }


def no_comparador(estado: dict):

    classificacao_manual = estado.get(
        "classificacao_manual",
        ""
    )

    comparacao = comparar_com_anotacao(
        estado["decisao_final"],
        classificacao_manual,
    )

    return {
        "comparacao": comparacao
    }

workflow.add_node(
    "Agente_1_Estruturador",
    no_agente_1_estruturador,
)

workflow.add_node(
    "Agente_2_Recuperador",
    no_agente_2_recuperador,
)

workflow.add_node(
    "Agente_3_Avaliador",
    no_agente_3_avaliador,
)

workflow.add_node(
    "Verificador",
    no_verificador,
)

workflow.add_node(
    "Comparador",
    no_comparador,
)

workflow.add_edge(START, "Agente_1_Estruturador")
workflow.add_edge("Agente_1_Estruturador", "Agente_2_Recuperador")
workflow.add_edge("Agente_2_Recuperador", "Agente_3_Avaliador")
workflow.add_edge("Agente_3_Avaliador", "Verificador")
workflow.add_edge("Verificador", "Comparador")
workflow.add_edge("Comparador", END)

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
        noticia = item["noticia_original"]
        entrada = {
            "noticia_original": noticia,
            "classificacao_manual": classificacao_manual,
        }

        print(
            f"[{i}/{len(noticias)}] {news_id} | "
            f"categoria: {noticia['categoria']}"
        )
        print(f"  Título: {noticia['titulo'][:80]}...")

        resultado = pipeline_compilado.invoke(entrada)
        decisao = resultado.get("decisao_final", {})
        verificacao = resultado.get("verificacao",{},)
        comparacao = resultado.get("comparacao",{},)
        estruturado = resultado.get("representacao_estruturado", {})
        recuperado = resultado.get("contexto_recuperado", {})
        exemplos = recuperado.get("exemplos", [])

        fatual = estruturado.get("elementos_factuais") or []
        fatual_txt = fatual if fatual else "(nenhum)"
        acrescenta = estruturado.get("resumo_acrescenta_info")
        apelo = estruturado.get("sinais_apelo_superficial")
        print(
            f"  Agente 1 →  tema: {estruturado.get('tema')}\n"
            f"             linguagem: {estruturado.get('tipo_linguagem')} | "
            f"elementos_factuais: {fatual_txt}\n"
            f"             resumo acrescenta: {acrescenta} | "
            f"apelo superficial: {apelo}\n"
        )

        print(f"  Agente 2 →  {len(exemplos)} exemplos recuperados:")
        for ex in exemplos:
            print(
                f"             [{ex.get('news_id')}] "
                f"{ex.get('classification')} | {ex.get('title', '')[:60]}"
            )
        
        print()

        print("Agente 3")

        print(
            f"  Classificação : {decisao.get('classificacao')}"
        )

        print(
            f"  Pontuação     : {decisao.get('pontuacao')}"
        )

        print(
            f"  Confiança     : {decisao.get('confianca'):.2f}"
        )

        print(
            f"  Revisão?      : {decisao.get('necessita_revisao')}"
        )

        print(
            f"  Justificativa : {decisao.get('justificativa')}"
        )

        print()

        print("Verificação")

        for problema in verificacao.get(
            "problemas",
            [],
        ):
            print("  •", problema)

        print()

        print("Comparação")

        print(
            f"Manual : {comparacao.get('classificacao_real')}"
        )

        print(
            f"Agente : {comparacao.get('classificacao_prevista')}"
        )

        print(
            f"Correto: {comparacao.get('correto')}"
        )

        print("\n" + "=" * 80 + "\n")

        print()


