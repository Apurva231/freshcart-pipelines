try:
    from mage_ai.data_preparation.decorators import data_loader, test
except ImportError:
    def data_loader(f): return f
    def test(f): return f

import pandas as pd
from sklearn.datasets import load_iris

@data_loader
def load_data(*args, **kwargs):
    iris = load_iris(as_frame=True)
    df = iris.frame.copy()
    df['species'] = df['target'].map(dict(enumerate(iris.target_names)))
    return df

@test
def test_output(output, *args):
    assert output is not None, "Output is None"
    assert len(output) == 150, f"Expected 150 rows, got {len(output)}"
    assert 'species' in output.columns, "Missing species column"
