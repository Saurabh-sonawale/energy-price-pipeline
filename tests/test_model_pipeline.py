import pandas as pd

from processing.feature_engineering import build_training_frame


def test_build_training_frame_for_prophet():
    df = pd.DataFrame(
        {
            "event_time": ["2025-01-01T00:00:00+00:00", "2025-01-01T01:00:00+00:00"],
            "price_mwh": [40.0, 41.5],
        }
    )
    frame = build_training_frame(df)
    assert list(frame.columns) == ["ds", "y"]
    assert len(frame) == 2
