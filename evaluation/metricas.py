from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def calcular_metricas(
    classes_reais: list[str],
    classes_previstas: list[str],
):
    """
    Calcula todas as métricas do projeto.
    """

    accuracy = accuracy_score(
        classes_reais,
        classes_previstas,
    )

    precision = precision_score(
        classes_reais,
        classes_previstas,
        average="macro",
        zero_division=0,
    )

    recall = recall_score(
        classes_reais,
        classes_previstas,
        average="macro",
        zero_division=0,
    )

    f1 = f1_score(
        classes_reais,
        classes_previstas,
        average="macro",
        zero_division=0,
    )

    matriz = confusion_matrix(
        classes_reais,
        classes_previstas,
        labels=[
            "high",
            "medium",
            "low",
            "ambiguous",
        ],
    )

    relatorio = classification_report(
        classes_reais,
        classes_previstas,
        digits=3,
        zero_division=0,
    )

    return {
        "accuracy": accuracy,
        "precision_macro": precision,
        "recall_macro": recall,
        "f1_macro": f1,
        "confusion_matrix": matriz,
        "classification_report": relatorio,
    }


def imprimir_metricas(metricas: dict):

    print("=" * 50)

    print(f"Accuracy : {metricas['accuracy']:.3f}")

    print(f"Precision: {metricas['precision_macro']:.3f}")

    print(f"Recall   : {metricas['recall_macro']:.3f}")

    print(f"F1-score : {metricas['f1_macro']:.3f}")

    print()

    print("Matriz de Confusão")

    print(metricas["confusion_matrix"])

    print()

    print(metricas["classification_report"])