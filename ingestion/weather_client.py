import logging
import math
import random
from datetime import datetime, timezone
from typing import Any, Dict

from ingestion.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class OpenWeatherClient(BaseAPIClient):
    """OpenWeatherMap current-weather API client with simulation fallback."""

    def __init__(self, api_key: str, units: str = "metric", simulation_mode: bool = False) -> None:
        super().__init__("https://api.openweathermap.org/data/2.5")
        self.api_key = api_key
        self.units = units
        self.simulation_mode = simulation_mode or not bool(api_key) or api_key == "replace_me"

    def fetch_current_weather(self, city: str) -> Dict[str, Any]:
        if self.simulation_mode:
            return self._simulate(city)

        payload = self.get("weather", params={"q": city, "appid": self.api_key, "units": self.units})
        record = {
            "event_time": datetime.now(timezone.utc).isoformat(),
            "source": "openweathermap",
            "city": city,
            "temperature": payload["main"].get("temp"),
            "humidity": payload["main"].get("humidity"),
            "pressure": payload["main"].get("pressure"),
            "wind_speed": payload.get("wind", {}).get("speed"),
            "clouds": payload.get("clouds", {}).get("all"),
            "weather_main": payload.get("weather", [{}])[0].get("main"),
            "raw": payload,
        }
        logger.info("weather_fetched", extra={"ctx_city": city})
        return record

    def _simulate(self, city: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        hour = now.hour
        seasonal = 8 * math.sin((hour / 24) * 2 * math.pi)
        temperature = 18 + seasonal + random.gauss(0, 1.8)
        humidity = min(max(55 + random.gauss(0, 12), 15), 95)
        wind_speed = max(random.gauss(5, 2), 0)
        return {
            "event_time": now.isoformat(),
            "source": "simulated_openweather",
            "city": city,
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "pressure": round(1012 + random.gauss(0, 8), 2),
            "wind_speed": round(wind_speed, 2),
            "clouds": int(min(max(random.gauss(45, 25), 0), 100)),
            "weather_main": random.choice(["Clear", "Clouds", "Rain", "Mist"]),
            "raw": {"simulation": True},
        }
