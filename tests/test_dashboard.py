"""Checks for public reporting integrity and user-visible app behavior."""
import re
import unittest
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest
from dashboard_data import load_data, metric_row, display_value, delta_label
from test_access import authenticated_app

ROOT=Path(__file__).resolve().parents[1]

class ReportingChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames,cls.meta=load_data()
        cls.metrics=cls.frames["metrics"]

    def test_monthly_grain_and_missingness(self):
        m=self.metrics
        self.assertFalse(m.duplicated(["month","platform","metric"]).any())
        pending=m.data_status.str.startswith("pending")|m.data_status.eq("unavailable")
        self.assertTrue(m.loc[pending,"value"].isna().all())
        for month in self.meta["periods"]:
            self.assertEqual(len(m[m.month==month]),48)
            row=metric_row(m,month,"Instagram","follows")
            self.assertEqual(display_value(row),"Unavailable")

    def test_reconciled_activity(self):
        m=self.metrics
        for month in self.meta["periods"]:
            with self.subTest(month=month):
                val=lambda platform,key:metric_row(m,month,platform,key).value
                for table,total,key in [("website_pages","pageviews","views"),("website_buttons","button_clicks","clicks")]:
                    d=self.frames[table]
                    self.assertEqual(d[d.month==month][key].sum(),val("Squarespace",total))
                d=self.frames["website_sources"]
                self.assertEqual(d[(d.month==month)&(d.level=="channel")].visits.sum(),val("Squarespace","visits"))
                p=self.frames["payment_methods"]
                p=p[p.month==month]
                self.assertAlmostEqual(p.recorded_amount.sum(),val("HoneyBook","recorded_payment_total"),places=2)
                self.assertAlmostEqual(p.recorded_net_amount.sum()+p.transaction_fees.sum(),p.recorded_amount.sum(),places=2)
                leads=self.frames["crm_sources"]
                self.assertEqual(leads[leads.report_month==month].lead_records.sum(),val("HoneyBook","lead_records"))
                self.assertEqual(val("Instagram","views_combined"),val("Instagram","views_instagram_only")+val("Instagram","facebook_views_in_instagram_card"))
                daily=self.frames["social_daily"]
                daily=daily[(daily.month==month)&(daily.aggregation_to_month=="sum")]
                for (platform,key),d in daily.groupby(["platform","metric"]):
                    self.assertEqual(len(d),31)
                    self.assertEqual(d.value.sum(),val(platform,key))

    def test_comparison_semantics(self):
        get=lambda key,month:metric_row(self.metrics,month,"Squarespace",key)
        self.assertEqual(delta_label(get("visits","2026-08"),get("visits","2026-07")),"+19.3%")
        self.assertEqual(delta_label(get("bounce_rate","2026-08"),get("bounce_rate","2026-07")),"+6.92 pp")
        self.assertEqual(delta_label(get("button_clicks","2026-08"),get("button_clicks","2026-07")),"-36.4%")
        self.assertIsNone(delta_label(metric_row(self.metrics,"2026-08","Instagram","monthly_reach"),metric_row(self.metrics,"2026-07","Instagram","monthly_reach")))

    def test_public_data_boundary(self):
        self.assertEqual(len(list((ROOT/"data").glob("*.csv"))),7)
        prohibited={"email","client_name","contact_name","phone","payment_id","contact_id","source_filename","destination_url"}
        for name,data in self.frames.items():
            with self.subTest(file=name):
                self.assertFalse(set(data.columns)&prohibited)
                self.assertIsNone(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",data.to_csv(index=False)))

class AppChecks(unittest.TestCase):
    def test_both_months_and_every_section(self):
        app=authenticated_app()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,"384")
        self.assertEqual(app.metric[0].delta,"+19.3%")
        for month in ["2026-07","2026-08"]:
            app.sidebar.selectbox(key="month").set_value(month).run()
            for section in ["Overview","Social","Website","Leads & payments","Data coverage"]:
                with self.subTest(month=month,section=section):
                    app.sidebar.radio(key="section").set_value(section).run(timeout=30)
                    self.assertFalse(app.exception)
                    if month=="2026-07":
                        self.assertTrue(all(not metric.delta for metric in app.metric))

    def test_social_platform_and_daily_scope(self):
        app=authenticated_app()
        app.sidebar.radio(key="section").set_value("Social").run()
        self.assertEqual(app.metric[0].value,"9,968")
        self.assertEqual(app.metric[5].value,"Unavailable")
        app.selectbox(key="daily_Instagram").set_value("views_combined").run()
        self.assertTrue(any("includes Facebook" in item.value for item in app.info))
        app.radio(key="social_platform").set_value("Facebook").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,"3,223")
        app.sidebar.toggle(key="compare").set_value(False).run()
        self.assertTrue(all(not metric.delta for metric in app.metric))

if __name__=="__main__":
    unittest.main()
