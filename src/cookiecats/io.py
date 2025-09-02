from pathlib import Path
import pandas as pd


# Load the Cookie Cats dataset
def load_cookiecats(csv_path: str | None = None) -> pd.DataFrame:
    if csv_path:
        path = Path(csv_path)
    else:
        # search common locations
        root = Path(__file__).resolve().parents[2]
        candidates = [
            root / "cookie_cats.csv",
            root / "data" / "cookie_cats.csv",
            root / "data" / "raw" / "cookie_cats.csv",
            root / "data" / "external" / "cookie_cats.csv",
        ]
        path = next((p for p in candidates if p.exists()), None)

    if not path or not path.exists():
        raise FileNotFoundError(
            "cookie_cats.csv not found. Pass csv_path or place in repo/data."
        )
    df = pd.read_csv(path)

    return df
