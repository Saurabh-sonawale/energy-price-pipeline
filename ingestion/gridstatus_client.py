import logging
import math
import random
from datetime import datetime, timezone
from typing import Any, Dict

from ingestion.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class GridStatusClient(BaseAPIClient):
    """Energy/grid price client.

    Public energy APIs differ by ISO and entitlement. For a reliable portfolio demo,
    this client supports simulation by default and keeps a single method boundary that
    can later be replaced with gridstatus.io or an ISO-specific endpoint.
    """

    def __init__(self, api_key: str = "", simulation_mode: bool = True) -> None:
        super().__init__("https://api.gridstatus.io")
        self.api_key = api_key
        self.simulation_mode = simulation_mode or not bool(api_key) or api_key == "replace_me_optional"

    def fetch_latest_price(self, market: str, location: str) -> Dict[str, Any]:
        if self.simulation_mode:
            return self._simulate(market, location)

        headers = {"Authorization": f"Bearer {self.api_key}"}
        # Endpoint shape is intentionally isolated because GridStatus product endpoints can vary by plan.
        payload = self.get("v1/datasets/lmp/latest", params={"market": market, "location": location}, headers=headers)
        return {
            "event_time": datetime.now(timezone.utc).isoformat(),
            "source": "gridstatus",
            "market": market,
            "location": location,
            "price_mwh": payload.get("price_mwh") or payload.get("lmp"),
            "demand_mw": payload.get("demand_mw"),
            "fuel_mix_gas_pct": payload.get("fuel_mix_gas_pct"),
            "raw": payload,
        }

    def _simulate(self, market: str, location: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        hour = now.hour
        day_cycle = 18 * math.sin(((hour - 15) / 24) * 2 * math.pi)
        peak_premium = 20 if 16 <= hour <= 21 else 0
        demand_mw = 19000 + 3500 * math.sin(((hour - 14) / 24) * 2 * math.pi) + random.gauss(0, 700)
        price = 45 + day_cycle + peak_premium + 0.0012 * (demand_mw - 19000) + random.gauss(0, 4)
        if random.random() < 0.02:
            price += random.choice([25, -15])
        return {
            "event_time": now.isoformat(),
            "source": "simulated_gridstatus",
            "market": market,
            "location": location,
            "price_mwh": round(max(price, 0), 2),
            "demand_mw": round(max(demand_mw, 0), 2),
            "fuel_mix_gas_pct": round(min(max(random.gauss(42, 8), 5), 85), 2),
            "raw": {"simulation": True},
        }
