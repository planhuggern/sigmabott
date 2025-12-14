from typing import Any

from pathlib import Path
from datetime import datetime, timezone, timedelta
import pandas as pd


def read_parquet_cache(path: str, max_age_s: int = 0):
    """
    Leser en Parquet-fil hvis den finnes og er fersk nok.

    Args:
        path (Path | str): sti til fil
        max_age_s (float | None): maks alder i sekunder før nedlasting kreves

    Returns:
        DataFrame | None  (None hvis ingen gyldig cache)
    """
    in_path = Path(path).with_suffix(".parquet")
    if not in_path.exists():
        return None

    df: pd.DataFrame = pd.read_parquet(in_path)  # type: ignore[reportUnknownMemberType]
    meta = df.attrs or {}
    last_fetch = meta.get("last_fetch")

    if max_age_s and last_fetch:
        naa = datetime.now(timezone.utc)
        siste = datetime.fromisoformat(last_fetch)
        age = naa - siste

        print(
            f"last_fetch: {siste}, now: {naa}, and age: {age} max age {timedelta(seconds=max_age_s)}"
        )
        if age > timedelta(seconds=max_age_s):
            return None
    return df


def write_parquet_cache(
    df: pd.DataFrame, path: str, **meta: str | float | int | Any
) -> None:
    """
    Skriver DataFrame til Parquet med metadata.

    Eksempel:
        write_parquet_cache(df, "data/BTC-USD_1h.parquet", symbols="BTC-USD", interval="1h")
    """
    outpath = Path(path).with_suffix(".parquet")
    outpath.parent.mkdir(parents=True, exist_ok=True)

    df = df.copy()
    meta["last_fetch"] = datetime.now(timezone.utc).isoformat()
    for k, v in meta.items():  # type: ignore
        df.attrs[k] = v

    df.to_parquet(outpath, index=True)
    print(f"💾 Lagret {outpath.name} ({len(df)} rader)")
