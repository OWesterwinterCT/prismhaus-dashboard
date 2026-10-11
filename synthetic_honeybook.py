"""Independent illustrative fixture. No real HoneyBook input is used here."""
import pandas as pd

NOTICE = "Illustrative HoneyBook data — not actual business results."
COLUMNS = ["month", "platform", "metric", "label", "value", "unit", "data_status",
           "precision", "aggregation", "scope", "dashboard_default"]
# Values chosen for the demo, independently of the agency's records.
PAYMENTS = [
    ("2026-07", "Credit card (demo)", 8, 12000, 11640, 360),
    ("2026-07", "Bank transfer (demo)", 3, 6000, 6000, 0),
    ("2026-08", "Credit card (demo)", 10, 16000, 15520, 480),
    ("2026-08", "Bank transfer (demo)", 5, 9000, 9000, 0),
]
SOURCES = [
    ("2026-07", "Referral (demo)", 10), ("2026-07", "Search (demo)", 8), ("2026-07", "Unknown (demo)", 6),
    ("2026-08", "Referral (demo)", 13), ("2026-08", "Search (demo)", 12), ("2026-08", "Unknown (demo)", 7),
]


def tables():
    methods = pd.DataFrame(PAYMENTS, columns=["month", "payment_method", "payment_count", "recorded_amount", "recorded_net_amount", "transaction_fees"])
    sources = pd.DataFrame(SOURCES, columns=["report_month", "lead_source", "lead_records"])
    records = []
    for month, projects, booked, filtered in [("2026-07", 40, 10, 6), ("2026-08", 48, 14, 9)]:
        p = methods[methods.month == month]
        s = sources[sources.report_month == month]
        entries = [
            ("lead_records", "CRM lead records (demo)", s.lead_records.sum(), "count", True, "Illustrative lead count; not linked to actual website visitors."),
            ("unknown_lead_source_records", "Unknown source (demo)", s[s.lead_source == "Unknown (demo)"].lead_records.sum(), "count", True, "Illustrative unknown-source count."),
            ("recorded_payment_total", "Recorded payment amount (demo)", p.recorded_amount.sum(), "USD", True, "Illustrative gross payments in USD; not attributed revenue."),
            ("recorded_payment_net", "Recorded net payment amount (demo)", p.recorded_net_amount.sum(), "USD", True, "Illustrative gross payments less fees, in USD."),
            ("recorded_payment_fees", "Payment transaction fees (demo)", p.transaction_fees.sum(), "USD", False, "Illustrative payment fees in USD."),
            ("payment_records", "Payment records (demo)", p.payment_count.sum(), "count", True, "Illustrative number of payment records."),
            ("card_payment_total", "Card payments (demo)", p[p.payment_method == "Credit card (demo)"].recorded_amount.sum(), "USD", False, "Illustrative card payments in USD."),
            ("manual_payment_total", "Manual payments (demo)", p[p.payment_method == "Bank transfer (demo)"].recorded_amount.sum(), "USD", False, "Illustrative bank transfers entered manually, in USD."),
            ("project_records_in_creation_export", "Project records (demo)", projects, "count", False, "Illustrative project cohort; not qualified leads."),
            ("booked_records_in_creation_export", "Booked project records (demo)", booked, "count", False, "Illustrative booked project status; not confirmed calls."),
            ("booked_in_month_within_creation_export_utc", "In-month booked projects (demo)", filtered, "count", False, "Illustrative subset of booked project records."),
            ("recorded_refunds", "Refunds (demo)", 0, "USD", False, "No refunds in this fictional example."),
            ("trade_flagged_amount", "Trade amount (demo)", 0, "USD", False, "No trade payments in this fictional example."),
            ("booked_calls", "Confirmed booked calls", None, "count", True, "Pending collection; not fabricated for this demo."),
            ("all_booked_projects", "All projects booked during month", None, "count", False, "Pending collection; not fabricated for this demo."),
            ("attributed_revenue", "Marketing-attributed revenue", None, "USD", False, "Pending linkage; no attribution inferred from synthetic data."),
        ]
        for metric, label, value, unit, default, scope in entries:
            records.append([month, "HoneyBook", metric, label, value, unit,
                            "synthetic" if value is not None else "pending_collection",
                            "illustrative" if value is not None else "not_available",
                            "demo_monthly" if value is not None else "unavailable", NOTICE + " " + scope, default])
    return pd.DataFrame(records, columns=COLUMNS), sources, methods


def validate_demo(metrics, sources, methods):
    expected, expected_sources, expected_methods = tables()
    hb = metrics[metrics.platform == "HoneyBook"]
    for actual, fixture, keys in [(hb, expected, ["month", "metric"]), (sources, expected_sources, ["report_month", "lead_source"]),
                                  (methods, expected_methods, ["month", "payment_method"])]:
        pd.testing.assert_frame_equal(actual.sort_values(keys).reset_index(drop=True), fixture.sort_values(keys).reset_index(drop=True), check_dtype=False)
