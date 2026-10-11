"""Export reviewed non-HoneyBook aggregates and always inject synthetic HoneyBook.

python tools/export_public_data.py /path/to/private-assembly/data
Real CRM lead or payment files are never opened by this exporter.
"""
from pathlib import Path
import argparse
import json
import re
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from synthetic_honeybook import tables

SCHEMAS = {
    "metrics.csv": ("monthly_metrics.csv", ["month","platform","metric","label","value","unit","data_status","precision","aggregation","scope","dashboard_default"]),
    "social_daily.csv": ("social_daily.csv", ["date","month","platform","metric","value","aggregation_to_month"]),
    "website_sources.csv": ("website_traffic_sources.csv", ["month","level","parent","source","visits"]),
    "website_pages.csv": ("website_pages.csv", ["month","page_key","page_label","views","time_on_page_seconds","bounce_rate","exit_rate"]),
    "website_buttons.csv": ("website_buttons.csv", ["month","placement_key","button_label","clicks","unique_views_as_reported","conversion_rate_as_reported","is_business_inquiry_destination"]),
}


def export(source: Path, destination: Path = ROOT / "data"):
    source, destination = Path(source), Path(destination)
    synthetic, sources, methods = tables()
    prepared = {}
    for output, (input_name, columns) in SCHEMAS.items():
        frame = pd.read_csv(source / input_name)[columns].copy()
        if output == "metrics.csv":
            # Discard all real HoneyBook rows, including hidden metrics and notes.
            frame = frame[frame.platform != "HoneyBook"]
            if set(frame.month) != set(synthetic.month):
                raise ValueError("This demo fixture covers July/August 2026 only. Extend it explicitly before adding months.")
            frame["scope"] = frame.scope.str.replace(r"\b\d{12,}\b", "(account)", regex=True)
            frame = pd.concat([frame, synthetic], ignore_index=True)
        if output == "website_sources.csv":
            frame = frame[frame.level.isin(["channel", "social_platform"])]
        text = frame.to_csv(index=False, na_rep="", float_format="%.10g")
        if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text):
            raise ValueError(f"Email-like text found in {output}; export stopped")
        prepared[output] = text
    prepared["crm_sources.csv"] = sources.to_csv(index=False)
    prepared["payment_methods.csv"] = methods.to_csv(index=False)
    metadata = json.loads((ROOT / "data/metadata.json").read_text())
    destination.mkdir(exist_ok=True, parents=True)
    for name, text in prepared.items():
        (destination / name).write_text(text, encoding="utf-8")
    (destination / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print("Exported non-HoneyBook aggregates and the independent HoneyBook demo fixture.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    export(parser.parse_args().source)
