from pathlib import Path
import pandas as pd

# -----------------------------
# Configuration
# -----------------------------
RAW_DATA_PATH = Path("data/raw")

# -----------------------------
# Read all CSV files
# -----------------------------
csv_files = sorted(RAW_DATA_PATH.glob("*.csv"))

print("=" * 100)
print("DATABASE SCHEMA REPORT")
print("=" * 100)

for file in csv_files:

    df = pd.read_csv(file, nrows=5)

    print(f"\n{'=' * 100}")
    print(f"TABLE : {file.stem}")
    print(f"{'=' * 100}")

    print(f"\nColumns ({len(df.columns)}):\n")

    for column in df.columns:
        print(f"• {column}")