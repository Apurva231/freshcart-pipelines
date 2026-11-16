# FreshCart Pipelines

A collection of data engineering pipelines built for the FreshCart platform, covering ELT ingestion, ML pipelines (Iris), real-time streaming with RabbitMQ, and CI/CD automation.

---

## Project Structure

```
freshcart-pipelines/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD workflow
├── elt/                        # ELT pipeline scripts (Snowflake)
├── iris_project/               # Mage-based Iris ML pipeline
│   └── transformers/
│       └── prepare_data.py     # Train/test split transformer
├── stream/                     # RabbitMQ streaming pipeline
├── tests/                      # Pytest test suite
│   └── test_prepare_data.py
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Components

### 1. ELT Pipeline (Snowflake)
Extracts raw FreshCart sales data, loads it into Snowflake staging tables, and applies SQL-based transformations to produce analytics-ready models.

- **Tool**: Python + `snowflake-connector-python`
- **Location**: `elt/`

### 2. Iris ML Pipeline (Mage)
A Mage-orchestrated pipeline that loads the Iris dataset, splits it into train/test sets (80/20), trains a classifier, and evaluates performance.

- **Tool**: Mage AI, scikit-learn, pandas
- **Location**: `iris_project/`
- **Key transformer**: `iris_project/transformers/prepare_data.py`

### 3. RabbitMQ Streaming Pipeline
Publishes and consumes FreshCart order events over a RabbitMQ message broker. Demonstrates real-time event-driven data ingestion.

- **Tool**: `pika` (RabbitMQ Python client)
- **Location**: `stream/`

### 4. CI/CD with GitHub Actions
Automated testing on every push using GitHub Actions. Installs dependencies and runs the full pytest suite.

- **Config**: `.github/workflows/ci.yml`

---

## Setup

### Prerequisites
- Python 3.12+
- pip
- (Optional) RabbitMQ server for streaming
- (Optional) Snowflake account credentials

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file (never committed) with your credentials:

```env
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=FRESHCART
SNOWFLAKE_SCHEMA=RAW
RABBITMQ_HOST=localhost
```

---

## Running Each Component

### Iris ML Pipeline (standalone)

```bash
python -c "
from sklearn.datasets import load_iris
from iris_project.transformers.prepare_data import transform
df = load_iris(as_frame=True).frame
result = transform(df)
print(result['split'].value_counts())
"
```

### Run Tests

```bash
python -m pytest tests/ -v
```

### ELT Pipeline

```bash
# (Scripts to be added in elt/)
python elt/run_elt.py
```

### Streaming Pipeline

```bash
# Start producer
python stream/producer.py
# Start consumer
python stream/consumer.py
```

---

## CI/CD

Every push to any branch triggers the GitHub Actions workflow defined in `.github/workflows/ci.yml`. It:
1. Checks out the code
2. Sets up Python 3.12
3. Installs all requirements
4. Runs `pytest tests/` to validate the pipeline logic

---

