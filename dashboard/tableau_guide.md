# Tableau Dashboard Guide

## Option A: Connect Tableau directly to PostgreSQL

1. Start the stack:
   ```bash
   docker compose up --build
   ```
2. Open Tableau Desktop.
3. Choose **Connect > To a Server > PostgreSQL**.
4. Use:
   - Server: `localhost`
   - Port: `5432`
   - Database: `energy_pipeline`
   - Username: `energy_user`
   - Password: `energy_password`
5. Add the following tables:
   - `processed_data`
   - `forecasts`
   - `trading_signals`

## Option B: Export CSV files

Run:

```bash
mkdir -p data
cp .env.example .env
 docker compose --profile batch run --rm dashboard-export
```

CSV files will be generated in `data/`.

## Recommended Dashboards

### 1. Forecast vs Actual
- X-axis: `event_time`
- Actual: `processed_data.price_mwh`
- Forecast: `forecasts.yhat`
- Add confidence band using `yhat_lower` and `yhat_upper`

### 2. KPI Metrics
- MAE
- RMSE
- Average absolute forecast error
- Signal counts by BUY/SELL/HOLD

### 3. Trend and Seasonality
- Use `artifacts/forecast_components.csv` from training
- Plot `trend`, `daily`, and `weekly`

### 4. Trading Signals
- X-axis: `event_time`
- Y-axis: price
- Color by signal
- Add cumulative position from `position_mwh`

### 5. Anomaly Detection
- Use `processed_data.is_anomaly`
- Filter anomalies and inspect price spikes
