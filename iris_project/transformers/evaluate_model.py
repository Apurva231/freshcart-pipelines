try:
    from mage_ai.data_preparation.decorators import transformer, test
except ImportError:
    def transformer(f): return f
    def test(f): return f

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

@transformer
def transform(data, *args, **kwargs):
    # data is a list: [prepared_df, model]
    if isinstance(data, list):
        df, model = data[0], data[1]
    else:
        df, model = data, args[0] if args else None

    feature_cols = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
    test_df = df[df['split'] == 'test']
    X_test = test_df[feature_cols]
    y_test = test_df['target']

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=['setosa', 'versicolor', 'virginica'], output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    print("=== Confusion Matrix ===")
    print(cm)
    print("\n=== Classification Report ===")
    metrics_df = pd.DataFrame(report).transpose()
    print(metrics_df.to_string())
    print(f"\nOverall Accuracy: {acc:.4f}")

    return {
        'accuracy': acc,
        'confusion_matrix': cm.tolist(),
        'report': report
    }

@test
def test_output(output, *args):
    assert output is not None
    assert output['accuracy'] > 0.5, f"Accuracy too low: {output['accuracy']}"
