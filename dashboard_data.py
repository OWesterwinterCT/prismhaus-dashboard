"""Data formatting shared by the app and its checks."""
from pathlib import Path
import json
import math
import pandas as pd

DATA=Path(__file__).resolve().parent/"data"
FILES=["metrics","social_daily","website_sources","website_pages","website_buttons","crm_sources","payment_methods"]
MISSING={"unavailable":"Unavailable","pending_access":"Pending access","pending_collection":"Pending data","pending_confirmation":"Unconfirmed"}

def load_data():
    frames={name:pd.read_csv(DATA/f"{name}.csv") for name in FILES}
    metadata=json.loads((DATA/"metadata.json").read_text())
    return frames,metadata

def month_name(month,short=False):
    return pd.Period(month,freq="M").strftime("%b %Y" if short else "%B %Y")

def previous_month(month,available):
    prior=str(pd.Period(month,freq="M")-1)
    return prior if prior in available else None

def metric_row(metrics,month,platform,key):
    rows=metrics[(metrics.month==month)&(metrics.platform==platform)&(metrics.metric==key)]
    if len(rows)!=1:
        raise ValueError(f"Expected one metric for {month}/{platform}/{key}; found {len(rows)}")
    return rows.iloc[0]

def display_value(row):
    if pd.isna(row.value): return MISSING.get(row.data_status,"Unavailable")
    if row.data_status=="rounded": return f"≈{row.value/1000:,.1f}K" if row.value>=1000 else f"≈{row.value:,.0f}"
    if row.unit=="proportion":return f"{row.value:.2%}"
    if row.unit=="currency_unconfirmed":return f"{row.value:,.2f}"
    if row.unit=="seconds":return f"{row.value:,.0f}s"
    return f"{row.value:,.0f}"

def delta_label(current,previous):
    if previous is None or pd.isna(current.value) or pd.isna(previous.value):return None
    if current.data_status=="rounded" or previous.data_status=="rounded":return None
    difference=float(current.value-previous.value)
    if current.unit=="proportion":return f"{difference*100:+.2f} pp"
    if previous.value==0:return "No change" if current.value==0 else f"{difference:+,.0f} (from zero)"
    return f"{difference/previous.value:+.1%}"

def public_monthly_table(metrics,month):
    frame=metrics[(metrics.month==month)&metrics.dashboard_default].copy()
    frame["Value"]=frame.apply(display_value,axis=1)
    return frame.rename(columns={"platform":"Platform","label":"Metric","data_status":"Status","scope":"Definition"})[["Platform","Metric","Value","Status","Definition"]]
