"""Convert the UCI Online Retail II Excel workbook to CSV (one file per sheet).

Usage:
    python scripts/convert_uci_xlsx.py --input /path/to/online_retail_II.xlsx --output data/raw/uci
"""

import argparse
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="data/raw/uci")
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    xl = pd.ExcelFile(args.input)
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        safe = sheet.replace(" ", "_").lower()
        target = out / f"online_retail_{safe}.csv"
        df.to_csv(target, index=False)
        print(f"wrote {target} ({len(df)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())