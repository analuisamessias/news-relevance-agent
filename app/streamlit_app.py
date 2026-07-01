import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.pipeline import pipeline_compilado


st.set_page_config(
    page_title="Sistema de Avaliação de Relevância Informacional",
    page_icon="📰",
    layout="wide",
)

st.title("📰 Sistema de Avaliação de Relevância Informacional")

st.markdown(
"""
Este sistema utiliza três agentes para avaliar a informatividade
de notícias.

Fluxo:

Notícia → Agente 1 → Agente 2 → Agente 3 → Verificação
"""
)

st.divider()

titulo = st.text_input("Título")

resumo = st.text_area(
    "Resumo",
    height=200,
)

categoria = st.text_input(
    "Categoria",
    value="news"
)

if st.button("Avaliar notícia"):

    entrada = {
        "noticia_original": {
            "titulo": titulo,
            "resumo": resumo,
            "categoria": categoria,
        },
        "classificacao_manual": "",
    }

    with st.spinner("Executando pipeline..."):

        resultado = pipeline_compilado.invoke(entrada)

    estruturado = resultado["representacao_estruturado"]
    contexto = resultado["contexto_recuperado"]
    decisao = resultado["decisao_final"]
    verificacao = resultado["verificacao"]

    st.success("Pipeline executado com sucesso!")

    st.divider()

    st.header("Agente 1 — Estruturação")

    st.json(estruturado)

    st.divider()

    st.header("Agente 2 — Contexto Recuperado")

    exemplos = contexto.get("exemplos", [])

    st.write(f"Exemplos recuperados: {len(exemplos)}")

    for exemplo in exemplos:

        with st.expander(exemplo["news_id"]):

            st.write(
                f"**Título:** {exemplo['title']}"
            )

            st.write(
                f"**Classificação:** {exemplo['classification']}"
            )

            st.write(
                exemplo["justification"]
            )

    st.divider()

    st.header("Agente 3 — Avaliação")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Classificação",
        decisao["classificacao"]
    )

    c2.metric(
        "Pontuação",
        f"{decisao['pontuacao']:.1f}"
    )

    c3.metric(
        "Confiança",
        f"{decisao['confianca']:.2f}"
    )

    st.subheader("Critérios utilizados")

    st.write(decisao["criterios_utilizados"])

    st.subheader("Justificativa")

    st.info(decisao["justificativa"])

    st.divider()

    st.header("Verificação")

    if verificacao["valida"]:

        st.success("Avaliação consistente.")

    else:

        st.warning("Revisão humana recomendada.")

        for problema in verificacao["problemas"]:

            st.write("•", problema)