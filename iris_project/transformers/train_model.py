try:
    from mage_ai.data_preparation.decorators import transformer, test
except ImportError:
    def transformer(f): return f
    def test(f): return f

import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

@transformer
def transform(df, *args, **kwargs):
    max_depth = int(kwargs.get('max_depth', 3))

    feature_cols = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test']

    X_train = train_df[feature_cols]
    y_train = train_df['target']
    X_test = test_df[feature_cols]
    y_test = test_df['target']

    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)

    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc = accuracy_score(y_test, model.predict(X_test))

    print(f"max_depth={max_depth}")
    print(f"Train accuracy: {train_acc:.4f}")
    print(f"Test accuracy:  {test_acc:.4f}")

    return [df, model]

@test
def test_output(output, *args):
    df, model = output[0], output[1]
    feature_cols = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
    test_df = df[df['split'] == 'test']
    from sklearn.metrics import accuracy_score
    acc = accuracy_score(test_df['target'], model.predict(test_df[feature_cols]))
    assert acc >= 0.80, f"Test accuracy {acc:.4f} < 0.80 threshold — pipeline halted"
