try:
    from mage_ai.data_preparation.decorators import data_exporter, test
except ImportError:
    def data_exporter(f): return f
    def test(f): return f

import pandas as pd
import os

@data_exporter
def export_data(data, *args, **kwargs):
    if isinstance(data, list):
        df, model = data[0], data[1]
    else:
        df, model = data, args[0] if args else None

    feature_cols = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
    test_df = df[df['split'] == 'test'].copy()
    X_test = test_df[feature_cols]

    test_df['predicted'] = model.predict(X_test)
    test_df['predicted_species'] = test_df['predicted'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})

    output_path = kwargs.get('output_path', 'iris_predictions.csv')
    test_df.to_csv(output_path, index=False)
    print(f"Saved {len(test_df)} predictions to {output_path}")
    return test_df

@test
def test_output(output, *args):
    assert output is not None
    assert len(output) > 0, "No predictions saved"
    assert 'predicted' in output.columns, "Missing predicted column"
