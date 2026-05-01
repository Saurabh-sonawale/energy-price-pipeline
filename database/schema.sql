CREATE TABLE IF NOT EXISTS raw_data (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_data_event_time ON raw_data(event_time);
CREATE INDEX IF NOT EXISTS idx_raw_data_topic ON raw_data(topic);

CREATE TABLE IF NOT EXISTS processed_data (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL UNIQUE,
    market VARCHAR(50),
    location VARCHAR(100),
    price_mwh DOUBLE PRECISION NOT NULL,
    demand_mw DOUBLE PRECISION,
    fuel_mix_gas_pct DOUBLE PRECISION,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    price_lag_1 DOUBLE PRECISION,
    price_lag_3 DOUBLE PRECISION,
    price_rolling_3 DOUBLE PRECISION,
    price_rolling_24 DOUBLE PRECISION,
    hour INTEGER,
    day_of_week INTEGER,
    week_of_year INTEGER,
    is_weekend INTEGER,
    is_anomaly BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_processed_data_event_time ON processed_data(event_time);

CREATE TABLE IF NOT EXISTS forecasts (
    id BIGSERIAL PRIMARY KEY,
    forecast_time TIMESTAMPTZ NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    yhat DOUBLE PRECISION NOT NULL,
    yhat_lower DOUBLE PRECISION,
    yhat_upper DOUBLE PRECISION,
    model_version VARCHAR(128),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_forecasts_forecast_time ON forecasts(forecast_time);

CREATE TABLE IF NOT EXISTS trading_signals (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL,
    actual_price DOUBLE PRECISION NOT NULL,
    forecast_price DOUBLE PRECISION NOT NULL,
    signal VARCHAR(10) NOT NULL CHECK (signal IN ('BUY', 'SELL', 'HOLD')),
    position_mwh DOUBLE PRECISION DEFAULT 0,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trading_signals_event_time ON trading_signals(event_time);
