try:
    from mage_ai.data_preparation.decorators import transformer, test
except ImportError:
    def transformer(f): return f
    def test(f): return f

import pandas as pd
from sklearn.model_selection import train_test_split

@transformer
def transform(df, *args, **kwargs):
    test_size = float(kwargs.get('test_size', 0.2))
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=42)
    result = df.copy()
    result['split'] = 'test'
    result.loc[train_df.index, 'split'] = 'train'
    return result

@test
def test_output(output, *args):
    assert output is not None, "Output is None"
    assert len(output) > 0, "Output is empty"
    assert 'split' in output.columns, "Missing split column"
    assert set(output['split'].unique()) == {'train', 'test'}, "Split values wrong"
