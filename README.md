# Sistema de Avaliação de Relevância Informacional

Sistema multiagente para avaliação de relevância informacional em sistemas de recomendação.

## Visão Geral

Este projeto propõe um pipeline inteligente baseado em múltiplos agentes capaz de avaliar a relevância informacional de conteúdos jornalísticos.

O sistema analisa itens de notícia utilizando critérios estruturados de avaliação, como:

- Densidade informativa
- Confiabilidade
- Potencial formativo
- Diversidade temática
- Clareza e valor contextual

O objetivo do projeto é investigar como a “relevância informacional” pode ser transformada em um critério operacional, explicável e reutilizável em sistemas de recomendação.

---

## Arquitetura do Projeto

O sistema é composto por três agentes principais:

### Agente 1 — Interpretador de Conteúdo

Responsável por:

- Extrair atributos do conteúdo
- Estruturar metadados
- Identificar categorias e padrões de linguagem

### Agente 2 — Recuperador de Critérios e Contexto

Responsável por:

- Recuperar critérios de avaliação
- Consultar exemplos anotados
- Fornecer contexto para o processo de decisão

### Agente 3 — Avaliador de Relevância

Responsável por:

- Atribuir pontuações/classificações
- Gerar saídas explicáveis
- Detectar ambiguidades e casos de baixa confiança

---

## Tecnologias

- Python
- LangChain
- LangGraph
- Ollama
- Llama 3 / Mistral
- ChromaDB ou LlamaIndex
- Pandas
- Streamlit

---

## Datasets

---

## Objetivos

- Construir um pipeline de avaliação explicável com IA
- Comparar recomendação orientada por engajamento vs relevância informacional
- Produzir saídas rastreáveis e estruturadas
- Permitir revisão humana em casos ambíguos

---

## Estrutura do Repositório

---

## Autores

Ana Luisa Mendes, Clara Tavares, Laura Oliveira e Leticia Scofield

Projeto desenvolvido para a disciplina de Projeto de Agentes de Inteligência Artificial (2026/1) do curso de Ciência da Computação da Universidade Federal de Minas Gerais (UFMG).

## Datasets

Para evitar versionar arquivos grandes no Git, os datasets devem ser baixados via script.

1. Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Baixe todos os arquivos da pasta compartilhada para `data/` (o script tambem extrai os `.zip` automaticamente):

```bash
python3 scripts/download_data.py
```
