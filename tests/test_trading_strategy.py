from trading.strategy import TradingStrategy


def test_buy_signal_when_forecast_above_actual():
    strategy = TradingStrategy(buy_threshold=2, sell_threshold=2)
    signal = strategy.generate_signal("2025-01-01T00:00:00+00:00", actual_price=40, forecast_price=45)
    assert signal["signal"] == "BUY"
    assert signal["position_mwh"] == 1


def test_sell_signal_when_forecast_below_actual_and_position_allowed():
    strategy = TradingStrategy(buy_threshold=2, sell_threshold=2)
    signal = strategy.generate_signal("2025-01-01T00:00:00+00:00", actual_price=50, forecast_price=45)
    assert signal["signal"] == "SELL"
    assert signal["position_mwh"] == -1


def test_hold_signal_when_spread_inside_threshold():
    strategy = TradingStrategy(buy_threshold=5, sell_threshold=5)
    signal = strategy.generate_signal("2025-01-01T00:00:00+00:00", actual_price=50, forecast_price=52)
    assert signal["signal"] == "HOLD"
