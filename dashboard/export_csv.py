from pathlib import Path

from config.settings import get_settings
from database.db import Database


QUERIES = {
    "processed_data.csv": "SELECT * FROM processed_data ORDER BY event_time",
    "forecasts.csv": "SELECT * FROM forecasts ORDER BY forecast_time",
    "trading_signals.csv": "SELECT * FROM trading_signals ORDER BY event_time",
}


def main() -> None:
    settings = get_settings()
    db = Database(settings.database_url)
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    for filename, query in QUERIES.items():
        frame = db.read_sql(query)
        frame.to_csv(output_dir / filename, index=False)
        print(f"Exported {filename}: {len(frame)} rows")


if __name__ == "__main__":
    main()
