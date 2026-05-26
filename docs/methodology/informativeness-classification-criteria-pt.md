# Critérios de Classificação de Informatividade em Notícias

## 1. Objetivo
Este documento define o que será entendido, no escopo do projeto, por informatividade em notícias e estabelece critérios para sua classificação. O objetivo é fornecer uma base comum para a anotação manual de exemplos, para a construção da base de conhecimento do sistema e para a interpretação das saídas do agente.

## 2. Escopo dos dados analisados
A classificação será feita com base apenas nas informações disponíveis no dataset MIND, especialmente:

- título da notícia;
- abstract/resumo;
- categoria;
- subcategoria;
- entidades identificadas, quando necessário.

Como o dataset não fornece o corpo completo da notícia para análise, a classificação de informatividade será feita a partir do que é observável nesses campos. Portanto, o projeto não pretende avaliar a profundidade total da cobertura jornalística, mas sim o grau de informatividade do item de notícia tal como ele aparece no dataset.

## 3. Definição de informatividade
Neste projeto, a informatividade será entendida como o grau em que uma notícia, a partir de seu título, resumo e metadados, apresenta informação concreta, específica e compreensível, em vez de conteúdo mais vago, genérico ou predominantemente chamativo.

## 4. Níveis de classificação
A classificação será feita em quatro possibilidades.

### 4.1 Alta informatividade (`high`)
A notícia apresenta informação concreta e específica, permitindo compreender com clareza o tema ou evento principal. O resumo acrescenta contexto ou detalhe relevante, e o item não depende principalmente de apelo superficial para chamar atenção.

### 4.2 Média informatividade (`medium`)
A notícia apresenta alguma informação relevante e permite compreender o tema central, mas com menor detalhamento, densidade informativa ou especificidade. O resumo informa, mas de forma mais limitada ou resumida.

### 4.3 Baixa informatividade (`low`)
A notícia apresenta conteúdo vago, genérico, superficial ou excessivamente chamativo. O título e o resumo acrescentam pouca informação concreta, dificultando a compreensão clara do fato ou tema principal.

### 4.4 Ambígua (`ambiguous`)
A notícia apresenta sinais mistos e não permite uma classificação segura em `high`, `medium` ou `low`. Nesse caso, o item deve ser sinalizado para discussão posterior.

## 5. Critérios de apoio à classificação
A classificação deve ser orientada pelos seguintes critérios:

### 5.1 Especificidade
Avalia se a notícia traz informação concreta e definida, como nomes, eventos, ações, locais, instituições ou circunstâncias identificáveis.

Pergunta orientadora: A notícia informa algo específico ou permanece vaga?

### 5.2 Densidade informativa do resumo
Avalia se o abstract acrescenta conteúdo relevante ao título, oferecendo contexto, explicação ou detalhes adicionais.

Pergunta orientadora: O resumo acrescenta de fato informação relevante ou apenas repete o título?

### 5.3 Clareza do conteúdo principal
Avalia se é possível entender com clareza qual é o tema ou fato central da notícia.

Pergunta orientadora: Depois de ler título e resumo, fica claro do que a notícia trata?

### 5.4 Grau de apelo superficial
Avalia se o item parece priorizar chamar atenção de forma vaga ou sensacionalista, sem entregar conteúdo informativo correspondente.

Pergunta orientadora: O item parece mais voltado ao apelo do que à informação?

Esse critério funciona como um sinal negativo na classificação.

## 6. Regras de anotação
Para manter a consistência da anotação, devem ser seguidas as regras abaixo:

### 6.1 Unidade de análise
Cada anotação deve considerar o item de notícia como um todo, com base no título, resumo e metadados disponíveis.

### 6.2 Foco da decisão
A decisão deve se concentrar no grau de informatividade observável no item, e não em julgamentos amplos sobre a qualidade jornalística total da matéria.

### 6.3 Casos ambíguos
Quando a notícia apresentar sinais contraditórios ou insuficientes para uma classificação segura, deve ser marcada como ambígua (`ambiguous`).

### 6.4 Justificativa curta
A anotação deve registrar uma justificativa breve para a classificação atribuída, explicando por que o item foi classificado daquela forma.

### 6.5 Consistência
Os mesmos critérios devem ser aplicados a toda a amostra anotada, evitando mudar o padrão de decisão de item para item.

## 7. Formato esperado da saída final do sistema
A saída final do sistema deve seguir um formato estruturado e rastreável. Mesmo nesta documentação em português, os campos e valores padronizados devem permanecer em inglês para manter consistência com o pipeline e o banco de dados.

Deve conter pelo menos:

- `classification`: `high`, `medium`, `low` ou `ambiguous`;
- `justification`: explicação breve da decisão;
- `confidence`: `high`, `medium` ou `low`.

Exemplo de saída esperada:

```json
{
  "classification": "medium",
  "justification": "The title and summary make the topic clear, but provide limited additional detail.",
  "confidence": "medium"
}
```
