"""Export only approved aggregate columns from the private assembly package.

python tools/export_public_data.py ../prismhaus_draft_data_2026_07_08/data
"""
from pathlib import Path
import argparse
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "metrics.csv": ("monthly_metrics.csv", ["month","platform","metric","label","value","unit","data_status","precision","aggregation","scope","dashboard_default"]),
    "social_daily.csv": ("social_daily.csv", ["date","month","platform","metric","value","aggregation_to_month"]),
    "website_sources.csv": ("website_traffic_sources.csv", ["month","level","parent","source","visits"]),
    "website_pages.csv": ("website_pages.csv", ["month","page_key","page_label","views","time_on_page_seconds","bounce_rate","exit_rate"]),
    "website_buttons.csv": ("website_buttons.csv", ["month","placement_key","button_label","clicks","unique_views_as_reported","conversion_rate_as_reported","is_business_inquiry_destination"]),
    "crm_sources.csv": ("crm_lead_sources.csv", ["report_month","lead_source","lead_records"]),
}

def export(source: Path, destination: Path = ROOT / "data"):
    source=Path(source); destination=Path(destination)
    destination.mkdir(exist_ok=True,parents=True)
    written=[]
    for output,(input_name,columns) in SCHEMAS.items():
        frame=pd.read_csv(source/input_name)[columns].copy()
        if output=="metrics.csv":
            frame["scope"]=frame.scope.str.replace(r"\b\d{12,}\b", "(account)",regex=True)
        if output=="website_sources.csv":
            frame=frame[frame.level.isin(["channel","social_platform"])]
        text=frame.to_csv(index=False,na_rep="",float_format="%.10g")
        if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",text):
            raise ValueError(f"Email-like text found in {output}; public export stopped")
        (destination/output).write_text(text)
        written.append(output)
    payments=pd.read_csv(source/"crm_payments.csv")
    grouped=payments.groupby(["month","payment_method"],as_index=False).agg(
        payment_count=("record_id","size"),recorded_amount=("recorded_amount","sum"),
        recorded_net_amount=("recorded_net_amount","sum"),transaction_fees=("transaction_fee","sum"))
    grouped.to_csv(destination/"payment_methods.csv",index=False,float_format="%.10g")
    written.append("payment_methods.csv")
    metadata={"client":"PrismHaus","periods":sorted(pd.read_csv(source/"monthly_metrics.csv").month.unique()),
        "snapshot_date":"2026-09-20","report_status":"Draft","collection_status":"Pending",
        "currency_status":"Unconfirmed","refresh_mode":"Manual snapshot", "files":written,
        "coverage":[
            {"source":"Squarespace","status":"Available","detail":"Monthly traffic, all viewed pages and all positive button actions. External inquiry completions are not measured here."},
            {"source":"Facebook","status":"Available with limits","detail":"Daily exports and rounded monthly viewers."},
            {"source":"Instagram","status":"Available with limits","detail":"Instagram-only monthly views. Rounded reach. Follows unavailable. Daily exported views include Facebook."},
            {"source":"ClickFunnels","status":"Limited scope","detail":"Visibility Report 2026 funnel only. Workspace contacts are not monthly opt-ins."},
            {"source":"HoneyBook","status":"Available with limits","detail":"Monthly lead records and recorded payments. Currency and the August trade entry need confirmation. Booked calls are pending."},
            {"source":"Meta Ads","status":"Pending access","detail":"Advertising account access or monthly exports pending. No spend, CPL or ROAS shown."},
            {"source":"Website tracker","status":"Pending data","detail":"Tracking Sheet and provider details pending."},
            {"source":"GA4 / GTM","status":"Unconfirmed","detail":"Installation and access have not been verified."},
            {"source":"Email and other channels","status":"Pending data","detail":"Monthly exports and final reporting scope pending."},
            {"source":"Attribution","status":"Pending data","detail":"Cross-platform event linkage, confirmed calls and campaign-attributed revenue are unavailable."}
        ]}
    (destination/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(f"Exported {len(written)} aggregate tables and metadata to {destination}")

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path)
    export(parser.parse_args().source)
