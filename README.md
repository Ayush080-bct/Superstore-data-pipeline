# Superstore Data Engineering Pipeline

An end-to-end ETL and analytics project for processing Superstore data, performing exploratory data analysis (EDA), and preparing datasets for downstream machine learning and reporting.

## Project Overview

This project demonstrates practical data engineering workflows in Python, including extraction, cleaning, transformation, EDA, and pipeline-oriented project structure.

## Project Structure

```text
AdvancedPythonProject/
|-- README.md
|-- environment.yml
|-- api/
|   `-- main.py
|-- data/
|   |-- raw/
|   |   `-- SuperstoreData.csv
|   `-- processed/
|       `-- cleansuperstoredata.csv
|-- docs/
|   |-- Architecture.png
|   `-- README.md
|-- etl/
|   |-- __init__.py
|   |-- extractors.py
|   |-- transform.py
|   |-- load.py
|   |-- validate.py
|   `-- pipeline.py
|-- notebook/
|   `-- EDA.ipynb
|-- frontend/
|-- ml/
|   `-- ml.ipynb
`-- test.csv
```

## Implemented ETL Modules

### `etl/extractors.py`
- Function: `extract_data(file_path, encoded_system="ISO-8859-1")`
- Behavior:
	- Validates source file path
	- Reads CSV with configurable encoding
	- Logs row/column counts

### `etl/transform.py`
- Function: `transform(df, order_date_col="Order_Date", ship_date_col="Ship_Date", ...)`
- Behavior:
	- Parses order and ship date columns
	- Creates derived fields:
		- `Order_Year`, `Order_Month`, `Order_Weekday`
		- `Ship_Year`, `Ship_Month`, `Ship_Weekday`
	- Strips whitespace from categorical text columns
	- Converts categorical text to lowercase (optional)
	- Removes duplicates (optional)

### `etl/validate.py`
- Function: `validate_data(df, ...)`
- Behavior:
	- Checks empty dataframe
	- Checks required columns exist
	- Reports duplicate row count
	- Checks negative sales row count
	- Validates `Ship_Date >= Order_Date`

### `etl/load.py`
- Function: `load_data(df)`
- Behavior:
	- Saves processed CSV output to `data/processed/cleansuperstoredata.csv`
	- PostgreSQL loading scaffold exists and can be enabled

### `etl/pipeline.py`
- Function: `run_pipeline()`
- Behavior:
	- Runs end-to-end ETL steps in sequence:
		- Extract -> Transform -> Validate -> Load

## Data

- Raw input: `data/raw/SuperstoreData.csv`
- Current processed output: `data/processed/cleansuperstoredata.csv`
- Additional sample input used during development: `test.csv`

## EDA Highlights

- Sales trends and shipping-lag trends have been analyzed in `notebook/EDA.ipynb`.
- A concise trend summary is documented in `docs/README.md`.
- Detailed visual exploration remains in the notebook for reproducibility.

## ML Baseline (Implemented)

- Notebook: `ml/ml.ipynb`
- Current baseline:
	- Data preparation from processed dataset
	- Train/test split
	- Missing-value handling
	- MinMax scaling (numeric)
	- One-hot encoding (categorical)
	- Linear Regression model
	- Evaluation with MAE, RMSE, R2
	- Actual vs Predicted and residual plots

## Environment Setup

Prerequisites:
- Conda
- Python 3.9 (managed by `environment.yml`)

Create and activate environment:

```bash
conda env create -f environment.yml
conda activate pipeline
```

## Run What Exists Today

From project root:

```bash
python etl/extractors.py
python etl/transform.py
python etl/validate.py
python etl/load.py
python etl/pipeline.py
```

Open notebook for analysis:

```bash
jupyter notebook notebook/EDA.ipynb
jupyter notebook ml/ml.ipynb
```

## Project Roadmap

- [x] Implement pipeline orchestration in `etl/pipeline.py`
- [x] Add explicit validation checks in `etl/validate.py`
- [x] Add load target logic in `etl/load.py`
- [ ] Build FastAPI endpoints in `api/main.py`
- [ ] Add automated tests for ETL modules
- [ ] Expand project docs in `docs/README.md`
- [ ] Add scheduling, monitoring, and logging conventions

## Architecture Reference

- Diagram: `docs/Architecture.png`

High-level intended flow:
1. Extract source data
2. Transform and standardize fields
3. Validate quality constraints
4. Load curated dataset
5. Expose via API/reporting/ML workflows

