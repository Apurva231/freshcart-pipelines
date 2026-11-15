try:
    from mage_ai.data_preparation.decorators import data_exporter, test
except ImportError:
    def data_exporter(f): return f
    def test(f): return f

import pandas as pd

@data_exporter
def export_data(metrics, *args, **kwargs):
    if isinstance(metrics, dict) and 'report' in metrics:
        df = pd.DataFrame(metrics['report']).transpose()
        df['accuracy_overall'] = metrics['accuracy']
    else:
        df = pd.DataFrame([{'accuracy': metrics.get('accuracy', 0)}])

    output_path = kwargs.get('output_path', 'iris_metrics.csv')
    df.to_csv(output_path, index=True)
    print(f"Saved metrics to {output_path}")
    print(df.to_string())
    return df

@test
def test_output(output, *args):
    assert output is not None
    assert len(output) > 0
