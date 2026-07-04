from pathlib import Path

import pandas as pd

RAW_DATA_PATH = Path("data/raw")

csv_files = sorted(RAW_DATA_PATH.glob("*.csv"))

print("=" * 100)
print("DATA QUALITY REPORT")
print("=" * 100)

for file in csv_files:

    df = pd.read_csv(file)

    print("\n" + "=" * 80)
    print(file.name)
    print("=" * 80)

    print(f"Rows    : {df.shape[0]:,}")
    print(f"Columns : {df.shape[1]}")

    print("\nData Types")

    print(df.dtypes)

    print("\nMissing Values")

    print(df.isna().sum())