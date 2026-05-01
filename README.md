# Energy Price Forecasting and Trading Pipeline

Production-grade, end-to-end data engineering and ML engineering project for real-time energy price forecasting and trading signal generation.

The system ingests weather and energy/grid price data, streams events through Kafka, engineers streaming features, stores raw and processed records in PostgreSQL, trains a Prophet forecasting model, serves predictions, generates BUY/SELL/HOLD trading signals, logs experiments with MLflow, and supports Tableau dashboards.

> The repository runs in simulation mode by default, so it works even if API keys are unavailable or API access is rate-limited. Replace `.env` values to use live APIs.

---

## Objective

Design and implement a real-time pipeline that:

- Ingests weather and energy price data via APIs
- Streams data using Apache Kafka
- Processes and engineers features
- Trains and serves a Prophet forecasting model
- Generates configurable trading signals
- Stores data in PostgreSQL
- Visualizes insights in Tableau
- Runs fully in containers using Docker
- Includes monitoring, logging, tests, CI, MLflow, and cloud deployment guidance

---

## Architecture

```text
+-------------------+        +------------------+        +-------------------+
|  OpenWeather API  | -----> | Weather Producer | -----> | weather-data topic|
+-------------------+        +------------------+        +-------------------+

+-------------------+        +----------------+          +--------------------+
| GridStatus / ISO  | -----> | Energy Producer| -------> | energy-prices topic|
| API or Simulator  |        +----------------+          +--------------------+
+-------------------+
                                      |
                                      v
                          +-----------------------+
                          | Kafka Stream Consumer |
                          +-----------------------+
                                      |
                                      v
                          +-----------------------+
                          | Feature Engineering   |
                          | - missing values      |
                          | - lag features        |
                          | - rolling averages    |
                          | - time features       |
                          | - anomaly detection   |
                          +-----------------------+
                                      |
                    +-----------------+-----------------+
                    |                                   |
                    v                                   v
          +-------------------+              +----------------------+
          | PostgreSQL        |              | processed-data topic |
          | raw_data          |              +----------------------+
          | processed_data    |                         |
          | forecasts         |                         v
          | trading_signals   |              +----------------------+
          +-------------------+              | Prediction Service   |
                    ^                         | Prophet model        |
                    |                         +----------------------+
                    |                                   |
                    |                                   v
                    |                         +----------------------+
                    +------------------------ | Trading Strategy     |
                                              | BUY / SELL / HOLD    |
                                              +----------------------+
                                                        |
                                                        v
                                             +-----------------------+
                                             | trading-signals topic |
                                             +-----------------------+
                                                        |
                                                        v
                                             +-----------------------+
                                             | Tableau Dashboard     |
                                             +-----------------------+
```

---

## Repository Structure

```text
energy-price-pipeline/
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
├── .env.example
├── config/
├── ingestion/
├── kafka/
├── processing/
├── models/
├── trading/
├── database/
├── orchestration/
├── dashboard/
├── docs/
├── tests/
├── notebooks/
└── .github/workflows/
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Python, Requests, OpenWeatherMap API, GridStatus-compatible client |
| Streaming | Apache Kafka, Confluent Kafka Python client |
| Processing | Pandas, streaming feature engineering |
| Storage | PostgreSQL |
| Forecasting | Prophet, scikit-learn metrics |
| Experiment Tracking | MLflow |
| Trading Logic | Configurable threshold strategy with risk limits |
| Visualization | Tableau via PostgreSQL or CSV export |
| Containers | Docker, Docker Compose |
| Orchestration | Cron example, optional Airflow DAG |
| CI/CD | GitHub Actions |
| Cloud Path | Google Cloud deployment guide |

---

## Quick Start

### 1. Clone and configure

```bash
cp .env.example .env
```

Simulation mode is enabled by default:

```env
SIMULATION_MODE=true
```

To use live weather data, set:

```env
OPENWEATHER_API_KEY=your_key
SIMULATION_MODE=false
```

Grid/energy data remains simulation-friendly because ISO and GridStatus API entitlements vary by plan.

### 2. Start the full pipeline

```bash
docker compose up --build
```

This starts:

- Zookeeper
- Kafka
- Kafka topic initialization
- PostgreSQL
- MLflow
- Weather producer
- Energy producer
- Stream processor
- Prediction service

### 3. Train the model

After the stream has produced enough rows:

```bash
docker compose --profile batch run --rm model-trainer
```

The trainer:

- Loads `processed_data`
- Prepares Prophet frame with `ds` and `y`
- Trains Prophet
- Validates with MAE and RMSE
- Saves model to `artifacts/prophet_model.pkl`
- Logs metrics and artifacts to MLflow

Open MLflow:

```text
http://localhost:5000
```

### 4. Export data for Tableau

```bash
mkdir -p data
docker compose --profile batch run --rm dashboard-export
```

CSV outputs:

```text
data/processed_data.csv
data/forecasts.csv
data/trading_signals.csv
```

---

## Kafka Topics

| Topic | Purpose |
|---|---|
| `weather-data` | Raw weather API records |
| `energy-prices` | Raw energy/grid price records |
| `processed-data` | Feature-engineered market records |
| `trading-signals` | BUY/SELL/HOLD strategy outputs |

Message schemas are stored in:

```text
kafka/schemas/
```

---

## Database Schema

PostgreSQL tables:

| Table | Purpose |
|---|---|
| `raw_data` | Stores original JSON payloads from Kafka |
| `processed_data` | Stores feature-engineered records |
| `forecasts` | Stores Prophet forecast outputs |
| `trading_signals` | Stores strategy outputs |

Schema file:

```text
database/schema.sql
```

---

## Feature Engineering

The streaming processor creates:

- Missing-value-safe weather joins
- Price lag features: `price_lag_1`, `price_lag_3`
- Rolling averages: `price_rolling_3`, `price_rolling_24`
- Time features: `hour`, `day_of_week`, `week_of_year`, `is_weekend`
- Anomaly flag using z-score against recent price history

Main file:

```text
processing/feature_engineering.py
```

---

## Forecasting Model

Prophet model pipeline:

1. Load processed records from PostgreSQL
2. Convert into Prophet format:
   - `ds`: timestamp
   - `y`: energy price
3. Train model with daily and weekly seasonality
4. Validate using MAE and RMSE
5. Save model artifact
6. Log parameters, metrics, and artifacts to MLflow
7. Export trend and seasonality components

Main file:

```text
models/train_prophet.py
```

---

## Prediction Service

The prediction service:

1. Consumes records from `processed-data`
2. Loads the trained Prophet model
3. Generates forecast for the event timestamp
4. Stores forecast in PostgreSQL
5. Passes actual and forecast prices to the trading strategy
6. Publishes signals to `trading-signals`

Main file:

```text
models/prediction_service.py
```

---

## Trading Strategy

Signal rules:

```text
BUY  if forecast > actual + BUY_THRESHOLD
SELL if forecast < actual - SELL_THRESHOLD
HOLD otherwise
```

Risk controls:

- Maximum long/short position limit
- Maximum daily trade count
- Configurable thresholds through `.env`

Main file:

```text
trading/strategy.py
```

---

## Tableau Dashboard

See:

```text
dashboard/tableau_guide.md
```

Recommended dashboards:

1. Forecast vs actual prices
2. MAE/RMSE KPI metrics
3. Trend and seasonality decomposition
4. Trading signals over time
5. Anomaly detection view

---

## Testing

Run locally:

```bash
pytest -q
```

Included tests:

- API client simulation shape
- Streaming feature engineering
- Prophet training frame preparation
- Trading signal logic

---

## Cloud Deployment on Google Cloud

See:

```text
docs/gcp_deployment.md
```

Suggested mapping:

- Cloud SQL for PostgreSQL
- Cloud Run or GKE for containers
- Secret Manager for API keys
- Cloud Scheduler or Composer for retraining
- Cloud Logging for observability
- Artifact Registry for container images
- Tableau connected to Cloud SQL or exported CSVs

---

## Monitoring and Logging

All services use structured JSON logging with fields such as:

- API failures
- Kafka delivery failures
- Stream processing errors
- Model training metrics
- Prediction and trading signal events

Logging setup:

```text
config/logging_config.py
```

---

## Production Design Notes

This project demonstrates production-oriented design decisions:

- Environment-based configuration
- API retry and rate-limit handling
- Simulation fallback for demo reliability
- Kafka topic separation by event type
- Idempotent-ish database upserts for processed records
- Structured logging for observability
- MLflow model tracking
- Dockerized local development
- CI test workflow
- GCP deployment mapping

For a true production trading system, add:

- Schema Registry
- Dead-letter Kafka topics
- Stronger exactly-once semantics
- Backtesting engine
- Market transaction-cost modeling
- Model registry promotion gates
- Feature store
- Secrets manager integration in runtime
- End-to-end data quality checks

---

## Resume-Ready Bullet Points

- Built an end-to-end real-time energy price forecasting pipeline using Python, Kafka, PostgreSQL, Docker, Prophet, and MLflow to ingest, process, model, and serve market signals.
- Engineered streaming features including lag prices, rolling averages, time-based seasonality indicators, weather joins, and anomaly flags for energy price forecasting.
- Designed Kafka-based event architecture with separate weather, energy, processed-data, and trading-signal topics to support scalable real-time processing.
- Implemented Prophet model training and validation with MAE/RMSE tracking, model artifact persistence, and MLflow experiment logging.
- Developed configurable BUY/SELL/HOLD trading signal logic with position limits and daily trade risk controls.
- Created PostgreSQL schemas and utility modules for raw ingestion records, processed features, forecasts, and trading signals.
- Containerized the full system with Docker Compose and documented Tableau and Google Cloud deployment workflows.

---

## Sample Output

Example processed record:

```json
{
  "event_time": "2025-01-01T18:00:00+00:00",
  "market": "nyiso",
  "location": "NYC",
  "price_mwh": 62.4,
  "demand_mw": 21340.2,
  "temperature": 21.5,
  "price_lag_1": 58.7,
  "price_rolling_3": 59.8,
  "hour": 18,
  "day_of_week": 2,
  "is_weekend": 0,
  "is_anomaly": false
}
```

Example trading signal:

```json
{
  "event_time": "2025-01-01T18:00:00+00:00",
  "actual_price": 62.4,
  "forecast_price": 67.8,
  "signal": "BUY",
  "position_mwh": 1.0,
  "reason": "Forecast exceeds actual by 5.40, above buy threshold 3.00."
}
```

---

## License

MIT License. Use this as a portfolio project and extend it with real ISO data, backtesting, and deployment automation.
