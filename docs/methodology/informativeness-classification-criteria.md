# Informativeness Classification Criteria for News

## 1. Objective
This document defines what will be considered informativeness in news within the project scope and establishes classification criteria. The objective is to provide a shared baseline for manual annotation, knowledge-base construction, and interpretation of agent outputs.

## 2. Scope of Analyzed Data
Classification must be based only on information available in the MIND dataset, especially:

- news title;
- abstract/summary;
- category;
- subcategory;
- identified entities, when relevant.

Since the dataset does not provide the full article body for analysis, informativeness classification is based only on what is observable in those fields. Therefore, the project does not aim to evaluate full journalistic depth, but rather the informativeness level of each news item as it appears in the dataset.

## 3. Definition of Informativeness
In this project, informativeness is defined as the degree to which a news item, based on its title, summary, and metadata, provides concrete, specific, and understandable information rather than vague, generic, or mostly attention-grabbing content.

## 4. Classification Levels
Classification is performed with four possible labels:

### 4.1 High Informativeness (`high`)
The news item provides concrete and specific information, allowing clear understanding of the main topic or event. The summary adds relevant context or details, and the item does not rely mainly on superficial appeal.

### 4.2 Medium Informativeness (`medium`)
The news item provides relevant information and allows understanding of the central topic, but with lower detail, lower information density, or lower specificity. The summary informs, but in a more limited way.

### 4.3 Low Informativeness (`low`)
The news item is vague, generic, superficial, or excessively attention-driven. Title and summary add little concrete information, making clear understanding of the main fact or topic difficult.

### 4.4 Ambiguous (`ambiguous`)
The news item shows mixed signals and does not allow a confident classification as high, medium, or low informativeness. In this case, the item should be flagged for later discussion.

## 5. Supporting Criteria for Classification
Classification should be guided by the following criteria:

### 5.1 Specificity
Checks whether the item includes concrete and defined information, such as names, events, actions, places, institutions, or identifiable circumstances.

Guiding question: Does the item provide specific information, or does it remain vague?

### 5.2 Summary Information Density
Checks whether the abstract adds relevant content to the title by providing context, explanation, or additional details.

Guiding question: Does the summary truly add relevant information, or does it mostly repeat the title?

### 5.3 Clarity of the Main Content
Checks whether the main topic or fact of the news item is clearly understandable.

Guiding question: After reading title and summary, is it clear what the news is about?

### 5.4 Degree of Superficial Appeal
Checks whether the item seems to prioritize vague or sensational attention-grabbing language without corresponding informative content.

Guiding question: Is the item more focused on appeal than information?

This criterion acts as a negative signal in the final classification.

## 6. Annotation Rules
To maintain annotation consistency, follow the rules below:

### 6.1 Unit of Analysis
Each annotation must consider the news item as a whole, based on the available title, summary, and metadata.

### 6.2 Decision Focus
The decision must focus on observable informativeness in the item, not on broad judgments about overall journalistic quality.

### 6.3 Ambiguous Cases
When the item has contradictory or insufficient signals for a confident decision, it must be labeled as ambiguous.

### 6.4 Short Justification
Each annotation must include a short justification explaining why the item received that classification.

### 6.5 Consistency
The same criteria must be applied across the annotated sample, avoiding decision-pattern drift from item to item.

## 7. Expected Format of System Output
The system output must follow a structured and traceable format containing at least:

- `classification`: `high`, `medium`, `low`, or `ambiguous`;
- `justification`: short explanation of the decision;
- `confidence`: `high`, `medium`, or `low`.

Expected output example:

```json
{
  "classification": "medium",
  "justification": "The title and summary make the topic clear, but provide limited additional detail.",
  "confidence": "medium"
}
```
