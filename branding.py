"""Display the supplied logo unchanged, fitting its transparent canvas in the UI."""
import base64
from functools import lru_cache
from pathlib import Path
import streamlit as st


@lru_cache(maxsize=1)
def logo_uri():
    original = Path(__file__).resolve().parent / "assets" / "PrismHaus-18.png"
    return "data:image/png;base64," + base64.b64encode(original.read_bytes()).decode("ascii")


def brand():
    # viewBox trims empty canvas only at display time; PNG bytes stay unchanged.
    st.markdown(f'''<div style="display:flex;align-items:center;gap:12px;margin:4px 0 14px">
    <svg width="40" height="48" viewBox="648 581 751 886" role="img" aria-label="PrismHaus logo">
    <image href="{logo_uri()}" width="2047" height="2048" /></svg>
    <span style="font-size:25px;font-weight:850;letter-spacing:-1.5px;color:#242838">PRISMHAUS<span style="color:#FF0080">.</span></span>
    </div>''', unsafe_allow_html=True)
