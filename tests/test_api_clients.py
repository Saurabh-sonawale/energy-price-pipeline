from ingestion.gridstatus_client import GridStatusClient
from ingestion.weather_client import OpenWeatherClient


def test_weather_client_simulation_shape():
    client = OpenWeatherClient(api_key="", simulation_mode=True)
    record = client.fetch_current_weather("New York")
    assert record["city"] == "New York"
    assert "temperature" in record
    assert "event_time" in record


def test_gridstatus_client_simulation_shape():
    client = GridStatusClient(api_key="", simulation_mode=True)
    record = client.fetch_latest_price("nyiso", "NYC")
    assert record["market"] == "nyiso"
    assert record["location"] == "NYC"
    assert record["price_mwh"] >= 0
