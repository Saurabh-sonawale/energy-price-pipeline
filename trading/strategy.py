from dataclasses import dataclass
from datetime import date
from typing import Dict


@dataclass
class TradingStrategy:
    """Simple threshold-based trading signal generator with basic risk controls."""

    buy_threshold: float = 3.0
    sell_threshold: float = 3.0
    max_position_mwh: float = 10.0
    max_daily_trades: int = 20
    current_position_mwh: float = 0.0
    trades_today: int = 0
    trade_date: date | None = None

    def generate_signal(self, event_time: str, actual_price: float, forecast_price: float) -> Dict:
        self._reset_daily_counter_if_needed(event_time)
        spread = forecast_price - actual_price

        if self.trades_today >= self.max_daily_trades:
            signal = "HOLD"
            reason = "Daily trade limit reached."
        elif spread > self.buy_threshold and self.current_position_mwh < self.max_position_mwh:
            signal = "BUY"
            self.current_position_mwh = min(self.current_position_mwh + 1.0, self.max_position_mwh)
            self.trades_today += 1
            reason = f"Forecast exceeds actual by {spread:.2f}, above buy threshold {self.buy_threshold:.2f}."
        elif spread < -self.sell_threshold and self.current_position_mwh > -self.max_position_mwh:
            signal = "SELL"
            self.current_position_mwh = max(self.current_position_mwh - 1.0, -self.max_position_mwh)
            self.trades_today += 1
            reason = f"Forecast below actual by {abs(spread):.2f}, above sell threshold {self.sell_threshold:.2f}."
        else:
            signal = "HOLD"
            reason = "Spread is within threshold or position limit reached."

        return {
            "event_time": event_time,
            "actual_price": actual_price,
            "forecast_price": forecast_price,
            "signal": signal,
            "position_mwh": self.current_position_mwh,
            "reason": reason,
        }

    def _reset_daily_counter_if_needed(self, event_time: str) -> None:
        current_date = date.fromisoformat(event_time[:10])
        if self.trade_date != current_date:
            self.trade_date = current_date
            self.trades_today = 0
