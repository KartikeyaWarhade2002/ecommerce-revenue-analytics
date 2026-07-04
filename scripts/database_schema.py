from pathlib import Path
import pandas as pd

RAW_DATA_PATH = Path("data/raw")

csv_files = sorted(RAW_DATA_PATH.glob("*.csv"))

print("=" * 100)
print("DATABASE SCHEMA")
print("=" * 100)

for file in csv_files:

    df = pd.read_csv(file, nrows=5)

    print(f"\n{'='*80}")
    print(file.name)
    print(f"{'='*80}")

    for column in df.columns:
        print(column)