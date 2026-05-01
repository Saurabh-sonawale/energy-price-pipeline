from datetime import datetime, timezone

from processing.feature_engineering import StreamingFeatureEngineer


def test_streaming_feature_engineering_lags_and_weather():
    fe = StreamingFeatureEngineer()
    fe.update_weather({"temperature": 20, "humidity": 60, "wind_speed": 5})
    first = fe.transform_energy_record(
        {
            "event_time": datetime(2025, 1, 1, 12, tzinfo=timezone.utc).isoformat(),
            "market": "nyiso",
            "location": "NYC",
            "price_mwh": 40,
            "demand_mw": 20000,
            "fuel_mix_gas_pct": 45,
        }
    )
    second = fe.transform_energy_record(
        {
            "event_time": datetime(2025, 1, 1, 13, tzinfo=timezone.utc).isoformat(),
            "market": "nyiso",
            "location": "NYC",
            "price_mwh": 42,
            "demand_mw": 20100,
            "fuel_mix_gas_pct": 46,
        }
    )
    assert first["temperature"] == 20
    assert first["hour"] == 12
    assert second["price_lag_1"] == 40
    assert second["price_rolling_3"] == 40
