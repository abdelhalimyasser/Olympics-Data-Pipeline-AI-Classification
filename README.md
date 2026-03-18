# 🏅 Olympics Data Engineering Pipeline

> End-to-end ELT pipeline for historical Olympic medalist data — web scraping → Astro Airflow orchestration → dbt transformation → ML classification → Plotly Dash dashboard.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [dbt Models](#dbt-models)
- [Machine Learning](#machine-learning)
- [Dashboard](#dashboard)
- [Setup & Installation](#setup--installation)
- [Running the Pipeline](#running-the-pipeline)
- [Tech Stack](#tech-stack)

---

## Overview

This project builds a fully automated data pipeline around historical **Summer and Winter Olympic Games** data scraped from Wikipedia. It answers questions like:

- How have medal counts evolved across every edition of the Games?
- Which disciplines produce the most decorated athletes of all time?
- Can we predict whether a sport will be discontinued based on historical patterns?

The pipeline covers the full stack: extraction, orchestration, transformation, ML classification, and interactive visualization.

---

## Architecture

```
Wikipedia
    │
    ▼
scrapper.py          ← Python web scraping
    │
    ▼
Astronomer Astro (Airflow) ← orchestration (olympics_pipeline.py DAG)
    │
    ├──► dbt seeds/  ← raw CSV files loaded into DuckDB
    │        │
    │        ▼
    │    staging/    ← cleaning, type casting, regex parsing
    │        │
    │        ▼
    │    marts/      ← dashboard-ready flat tables
    │
    ├──► include/datasets/   ← exported CSVs for ML + dashboard
    │
    └──► Plotly Dash dashboard  ←  analytical + ML results
```

*ERD and data modeling diagram:*

![Database Modeling & ERD](data%20modling.jpg)

---

## Project Structure

```
├── dags/
│   ├── .airflowignore
│   └── olympics_pipeline.py          ← main Airflow DAG
│
├── dashboard/
│   └── dashboard.py                  ← Plotly Dash app
│
├── include/
│   ├── datasets/                     ← mart exports (CSVs for ML + dashboard)
│   │   ├── discontinued_sports.csv
│   │   ├── medalists_age.csv
│   │   ├── olympiad_summry.csv
│   │   └── sports_summry.csv
│   ├── models/                       ← serialized ML models
│   │   ├── decision_tree.pkl
│   │   ├── knn.pkl
│   │   ├── logistic_regression.pkl
│   │   ├── naive_bayes.pkl
│   │   ├── random_forest.pkl
│   │   └── svm.pkl
│   └── scrapper.py                   ← Wikipedia scraping logic
│
├── notebooks/
│   ├── classification.ipynb          ← ML model training & evaluation
│   ├── dashboard_graphs.ipynb        ← chart prototyping
│   └── wikipedia_olympic_medalists_webscrapping.ipynb
│
├── olympics_dbt/
│   ├── models/
│   │   ├── marts/
│   │   │   ├── discontinued_sports.sql
│   │   │   ├── medalists_age.sql
│   │   │   ├── olympiad_summry.sql
│   │   │   └── sports_summry.sql
│   │   └── staging/
│   │       ├── schema.yml
│   │       ├── stg_discontinued_summer_sports.sql
│   │       ├── stg_medalists_age_by_sport.sql
│   │       ├── stg_summer_sports_medalist_by_olympiad.sql
│   │       ├── stg_summer_sports_medalist_by_sport.sql
│   │       ├── stg_winter_sports_medalist_by_olympiad.sql
│   │       └── stg_winter_sports_medalist_by_sport.sql
│   ├── seeds/                        ← raw CSV seeds (6 files)
│   └── .gitignore
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── packages.txt
├── README.md
└── requirements.txt
```

---

## Data Flow

### 1. Extraction
`include/scrapper.py` scrapes 6 tables from Wikipedia into raw CSV files, which are loaded into dbt as **seeds**:

| Seed | Description | Rows |
|---|---|---|
| `raw_summer_sports_medalist_by_olympiad` | One row per Summer Games edition (1896–2024) | 30 |
| `raw_winter_sports_medalist_by_olympiad` | One row per Winter Games edition (1924–2026) | 25 |
| `raw_summer_sports_medalist_by_sport` | Cumulative totals per Summer discipline | 37 |
| `raw_winter_sports_medalist_by_sport` | Cumulative totals per Winter discipline | 16 |
| `raw_discontinued_summer_sports` | Disciplines no longer on the Summer programme | 10 |
| `raw_medalists_age_by_sport` | Age records (youngest/oldest) per sport | 24 |

### 2. Orchestration
The pipeline runs on **Astronomer Astro** (Astro CLI + Docker-based Airflow runtime). The DAG (`olympics_pipeline.py`) sequences:
1. Scraping → seed files
2. `dbt seed` → loads CSVs into DuckDB
3. `dbt run` → staging then marts
4. Export mart tables to `include/datasets/` for the dashboard

> dbt tasks inside the DAG are managed via **Astronomer Cosmos**, which renders each dbt model as an individual Airflow task with full lineage visibility in the Airflow UI.

### 3. Transformation (dbt)

**Staging layer** — cleaning only, no business logic:
- Strip Wikipedia footnote markers (`[a]`, `[d]`, etc.)
- Cast all numeric columns to correct types
- Parse athlete name + IOC country code from raw strings using regex
- Handle edge cases: `"see list"`, empty strings, `U+00A0` non-breaking spaces, dual-host cities (1956), multi-part host strings (1976)

**Marts layer** — dashboard-ready flat tables:

| Mart | Grain | Use |
|---|---|---|
| `olympiad_summry` | (year, season) | Medals trend, host map, top athlete per edition |
| `sports_summry` | (discipline, season) | Medals per sport, active vs discontinued |
| `discontinued_sports` | (discipline, year) | Timeline / Gantt chart |
| `medalists_age` | (medalist, title) | Youngest / oldest leaderboard |

---

## dbt Models

```
seeds (raw CSVs)
    └── staging (stg_*)      materialized as: view
            └── marts (*)    materialized as: table
```

Run tests with:
```bash
dbt test --select staging
```

Key data quality tests defined in `staging/schema.yml`:
- `not_null` and `unique` on all primary keys
- `accepted_values` on boolean flags (`has_total_mismatch`, etc.)
- Conditional `not_null` — e.g. athlete columns are only required where data is not `"see list"`

---

## Machine Learning

**Goal:** Classify whether a sport is likely to remain active or be discontinued based on historical statistical features.

**Features used:**
- Number of Olympic editions contested
- Total medals awarded
- Medal event types count
- First and last year contested

**Models trained** (see `notebooks/classification.ipynb`):

| Model | File |
|---|---|
| Logistic Regression | `logistic_regression.pkl` |
| Decision Tree | `decision_tree.pkl` |
| Random Forest | `random_forest.pkl` |
| K-Nearest Neighbors | `knn.pkl` |
| Naive Bayes | `naive_bayes.pkl` |
| Support Vector Machine | `svm.pkl` |

Serialized models are stored in `include/models/` and served live by the dashboard.

---

## Dashboard

Built with **Plotly Dash**, locally hosted. Covers two sections:

**Analytics:**
- Medals awarded per Games edition (line chart, filterable by season)
- Medal events growth over time
- Host city map
- Top athlete per edition cards
- Medals per discipline (treemap)
- Active vs discontinued sports breakdown

**ML Classification:**
- Input a discipline's statistics
- Get a real-time prediction from any of the 6 trained models
- Side-by-side model comparison

---

## Setup & Installation

### Prerequisites
- Docker
- [Astro CLI](https://docs.astronomer.io/astro/cli/install-cli)

### Start the Astro environment (recommended)

```bash
# Initialize (first time only)
astro dev init

# Start Airflow locally via Astro
astro dev start
```

Airflow UI will be available at `http://localhost:8080`
Default credentials: `admin` / `admin`

### Local setup

```bash
pip install -r requirements.txt

# Install system packages (if needed)
cat packages.txt | xargs apt-get install -y
```

### dbt setup

```bash
cd olympics_dbt

# Install dbt dependencies
dbt deps

# Load seeds
dbt seed

# Run models
dbt run

# Run tests
dbt test
```

---

## Running the Pipeline

**Full pipeline via Astro Airflow:**
1. Start the Astro environment: `astro dev start`
2. Open the Airflow UI at `http://localhost:8080`
3. Trigger the `olympics_pipeline` DAG from the UI, or via CLI:
```bash
astro dev start
```

**Dashboard only (after dbt):**
> run in venv or outside airflow to avoid conflicts
```bash
python dashboard/dashboard.py
```
Then open `http://localhost:8050` in your browser.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Scraping | Python (BeautifulSoup / requests) |
| Orchestration | Astronomer Astro (Airflow + Cosmos) |
| Warehouse | DuckDB |
| Transformation | dbt (with Cosmos for Airflow integration) |
| ML | scikit-learn |
| Dashboard | Plotly Dash |
| Containerization | Docker |
