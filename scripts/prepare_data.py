import pandas as pd

# Colunas: NewsID, Category, SubCategory, Title, Abstract, URL, TitleEntities, AbstractEntities
news = pd.read_csv("data/MINDsmall_train/news.tsv", sep="\t",
                   header=None,
                   names=["news_id","category","subcategory",
                          "title","abstract","url",
                          "title_entities","abstract_entities"])

print(news.shape)          # quantas notícias?
print(news.dtypes)         # tipos de colunas
print(news.head(3))        # primeiras linhas
print(news["category"].value_counts())   # distribuição por categoria
print(news["abstract"].isna().sum())     # quantos abstracts faltando?

def limpar_news(df):
    # Selecionar apenas campos úteis para o pipeline
    df = df[["news_id", "category", "subcategory", "title", "abstract"]].copy()
    
    # Remover linhas sem abstract (não classificáveis)
    df = df.dropna(subset=["abstract"])
    df = df[df["abstract"].str.strip() != ""]
    
    # Normalizar espaços extras e caracteres especiais
    df["title"]    = df["title"].str.strip()
    df["abstract"] = df["abstract"].str.strip()
    
    return df.reset_index(drop=True)

news_clean = limpar_news(news)
print(f"Antes: {len(news)} | Depois: {len(news_clean)}")
news_clean.to_csv("data/news_clean.csv", index=False)
print("news_clean.csv salvo.")

def amostrar_balanceado(df, n_por_categoria=50, seed=42):
    """Pega n notícias por categoria para garantir diversidade."""
    # Embaralha todo o DataFrame de forma aleatória
    df_embaralhado = df.sample(frac=1, random_state=seed)
    
    # Agrupa por categoria e pega os primeiros 'n' registros
    return (df_embaralhado.groupby("category")
                          .head(n_por_categoria)
                          .reset_index(drop=True))

amostra = amostrar_balanceado(news_clean, n_por_categoria=50)
print(amostra["category"].value_counts())

# Salvar subconjunto
amostra.to_csv("data/news_sample.csv", index=False)

# Separar ~30 para anotação manual (Pessoa 1 vai anotar isso)
anotacao = amostra.sample(30, random_state=42)
anotacao.to_csv("data/news_para_anotacao.csv", index=False)

def preparar_input(row):
    """Converte uma linha do DataFrame no formato de entrada do Agente 1."""
    return {
        "news_id":     row["news_id"],
        "category":    row["category"],
        "subcategory": row.get("subcategory", ""),
        "title":       row["title"],
        "abstract":    row["abstract"],
        # Texto concatenado para facilitar análise do agente
        "full_text":   f"{row['title']}. {row['abstract']}"
    }

# Gerar lista de inputs prontos para o pipeline
inputs_pipeline = [preparar_input(r) for _, r in amostra.iterrows()]

# Salvar como JSON (formato amigável para o pipeline da Pessoa 3)
import json
with open("data/pipeline_inputs.json", "w", encoding="utf-8") as f:
    json.dump(inputs_pipeline, f, ensure_ascii=False, indent=2)

print(f"{len(inputs_pipeline)} itens prontos para o pipeline.")