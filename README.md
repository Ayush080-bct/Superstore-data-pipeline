# Superstore Data Pipeline

End-to-end data engineering and analytics project built in Python with:
- ETL pipeline for Superstore data
- Flask API for pipeline control, analytics, and ML inference
- Frontend dashboard for visualization and operations
- EDA and ML notebooks for experimentation

## Features

- ETL pipeline: extract, transform, validate, and load curated data
- REST API for:
  - health check
  - ETL step execution
  - dataset access and stats
  - analytics endpoints
  - model retraining and sales prediction
- Browser dashboard in `frontend/`
- ML model lifecycle in `ml/model.py` with persisted artifacts in `ml/models/`

## Repository Structure

```text
AdvancedPythonProject/
|-- README.md
|-- QUICKSTART.md
|-- requirements.txt
|-- environment.yml
|-- api/
|   |-- main.py
|   `-- README.md
|-- data/
|   |-- raw/
|   |   |-- SuperstoreData.csv
|   |   `-- ebay_scraped.csv
|   `-- processed/
|       |-- cleansuperstoredata.csv
|       |-- cleandata.csv
|       `-- ebay_cleaned.csv
|-- etl/
|   |-- extractors.py
|   |-- transform.py
|   |-- validate.py
|   |-- load.py
|   |-- pipeline.py
|   `-- daily_report.py
|-- ml/
|   |-- model.py
|   |-- ml.ipynb
|   `-- models/
|-- notebook/
|   |-- EDA.ipynb
|   `-- Eda2.ipynb
|-- frontend/
|   |-- index.html
|   |-- app.js
|   `-- styles.css
|-- reports/
|   `-- sales_product_report.csv
`-- sources/
    |-- ebay_scraper.py
    `-- ebay_transform.py
```

## Quick Start

From the project root:

```bash
conda env create -f environment.yml
conda activate pipeline
```

If you prefer pip:

```bash
pip install -r requirements.txt
```

## Run the ETL Pipeline

```bash
python etl/pipeline.py
```

Default input and output:
- Input: `data/raw/SuperstoreData.csv`
- Output: `data/processed/cleansuperstoredata.csv`

## Run the API

```bash
python api/main.py
```

API base URL:
- `http://localhost:5000/api`

Health check:

```bash
curl http://localhost:5000/api/health
```

## Run the Frontend

In a separate terminal:

```bash
cd frontend
python -m http.server 8000
```

Open:
- `http://localhost:8000`

The frontend expects the API at:
- `http://localhost:5000/api`

## Core API Endpoints

Pipeline:
- `POST /api/pipeline/run`
- `POST /api/pipeline/extract`
- `POST /api/pipeline/transform`
- `POST /api/pipeline/validate`
- `POST /api/pipeline/load`

Data and analytics:
- `GET /api/data/superstore`
- `GET /api/data/stats`
- `GET /api/analytics/sales-trends`
- `GET /api/analytics/category-performance`
- `GET /api/analytics/regional-analysis`

ML:
- `GET /api/model/info`
- `GET /api/model/metrics`
- `POST /api/model/retrain`
- `POST /api/predict/sales`

For full request/response examples, see `api/README.md`.

## Notebooks

- EDA: `notebook/EDA.ipynb`
- Additional EDA: `notebook/Eda2.ipynb`
- ML experimentation: `ml/ml.ipynb`

## Documentation

- Quick setup and walkthrough: `QUICKSTART.md`
- API details: `api/README.md`
- Frontend usage: `frontend/README.md`
- EDA notes: `docs/README.md`

## Current Status

- Flask API is implemented and operational from `api/main.py`
- ETL orchestration is implemented in `etl/pipeline.py`
- Baseline sales prediction model is implemented in `ml/model.py`

## Notes

- This project is intended for learning and portfolio use.
- For best compatibility, use the provided conda environment.

