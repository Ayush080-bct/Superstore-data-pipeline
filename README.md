# Superstore Data Engineering Pipeline

An end-to-end ETL and analytics project for processing Superstore data, performing exploratory data analysis (EDA), and preparing datasets for downstream machine learning and reporting.

## Project Overview

This project demonstrates practical data engineering workflows in Python, including extraction, cleaning, transformation, EDA, and pipeline-oriented project structure.

## Project Structure

```
AdvancedPythonProject/
├── README.md                  # Project documentation
├── environment.yml            # Conda environment definition
├── api/
│   └── main.py               # API entrypoint
├── data/
│   ├── raw/
│   │   └── SuperstoreData.csv
│   └── processed/
├── docs/
│   ├── README.md
│   └── Architecture.png      # System architecture diagram
├── etl/
│   ├── __init__.py
│   └── extractors.py
├── notebook/
│   └── EDA.ipynb             # Exploratory data analysis
├── frontend/
└── ml/

```

The repository is actively evolving and more modules will be added.

## Architecture Flow

The pipeline follows this high-level flow:

1. Data Source (multiple sources)
2. Data Engineering Collection Layer
3. ETL Processing (Extract, Transform, Load)
4. Automated EDA and Machine Learning
5. Scheduling Method
6. Logging and Monitoring
7. Application and Report Delivery


## Data

**Source Dataset:** `data/raw/SuperstoreData.csv`
- Contains Superstore transaction and business data
- Used for ETL pipeline processing and analysis

**Output:** Processed data stored in `data/processed/`

## Documentation

See [docs/README.md](docs/README.md) for detailed documentation.

The project architecture is visualized in [Architecture.png](docs/Architecture.png).

## Getting Started

### Prerequisites
- Python 3.8+
- Conda installed

### Installation

```bash
cd AdvancedPythonProject
conda env create -f environment.yml
conda activate pipeline
```

## Current Progress

- Data loading utilities implemented in etl extractors
- EDA notebook created and executed
- Initial cleaning and quality checks completed:
	- Null and NA checks
	- Data type and shape inspection
	- Duplicate analysis
	- Postal_Code removal
- Distribution analysis added:
	- Boxplot and histogram visualizations
	- Sales outlier insight
	- Sales right-skew interpretation

## Project Status

In development
- Core ETL structure set up
- Data source configured
- Pipeline modules being developed

## Next Steps

- [ ] Implement transform.py with documented cleaning rules
- [ ] Add data validation and quality checks
- [ ] Add reproducible feature engineering steps
- [ ] Add tests for ETL functions
- [ ] Expose processed output through API endpoints
- [ ] Add reporting and model training workflow

