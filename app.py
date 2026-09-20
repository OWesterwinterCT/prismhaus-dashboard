"""Public, aggregate-only monthly reporting dashboard."""
import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_data import (
    load_data, month_name, previous_month, metric_row, display_value,
    delta_label, public_monthly_table,
)

st.set_page_config(page_title="PrismHaus | Monthly performance", page_icon="◒", layout="wide")
st.markdown("""
<style>
 .block-container {padding-top:2rem; padding-bottom:3rem; max-width:1500px;}
 h1 {letter-spacing:-.055em; font-weight:750 !important; padding-bottom:.35rem !important;}
 h2,h3 {letter-spacing:-.025em;}
 [data-testid="stMetricValue"] {font-size:1.95rem; letter-spacing:-.04em;}
 [data-testid="stMetricLabel"] {font-size:.83rem;}
 [data-testid="stMetric"] {background:white; border-color:#E3E2DD;}
 [data-testid="stSidebar"] {border-right:1px solid #E3E2DD;}
 .wordmark {font-size:1.6rem;font-weight:850;letter-spacing:-.07em;margin-bottom:0;}
 .kicker {color:#777980;font-size:.72rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;}
 .pill {display:inline-block;border-radius:30px;background:#F6E4EC;color:#9D2458;
        padding:.3rem .65rem;font-size:.73rem;font-weight:650;}
 .insight {background:#242838;color:#FAFAF8;border-radius:12px;padding:1.25rem 1.4rem;margin:1rem 0 1.5rem;}
 .insight strong {color:#F0B4CE;}
 .foot {border-top:1px solid #DEDED8;padding-top:1rem;color:#777980;font-size:.78rem;margin-top:2rem;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_data()

frames, meta = get_data()
metrics = frames["metrics"]
periods = sorted(meta["periods"])
PINK, TEAL, NAVY, GRAY = "#C62F70", "#167D8D", "#343A56", "#ABB0BA"

with st.sidebar:
    st.markdown('<div class="wordmark">PRISMHAUS<span style="color:#C62F70">.</span></div>', unsafe_allow_html=True)
    st.caption("Monthly performance dashboard")
    st.divider()
    month = st.selectbox("Reporting month", periods, index=len(periods)-1, format_func=month_name, key="month")
    prior = previous_month(month, periods)
    compare = st.toggle("Compare previous month", value=True, disabled=prior is None, key="compare") and prior is not None
    if prior is None:
        st.caption("Previous month has not been collected.")
    section = st.radio("Explore", ["Overview", "Social", "Website", "Leads & payments", "Data coverage"], key="section")
    st.divider()
    st.markdown('<span class="pill">DRAFT · COLLECTION PENDING</span>', unsafe_allow_html=True)
    st.caption("July–August 2026\n\nSnapshot: 20 September 2026\n\nManual refresh · aggregate data")
    st.download_button("Download monthly figures", public_monthly_table(metrics, month).to_csv(index=False),
                       file_name=f"prismhaus-{month}-metrics.csv", mime="text/csv", use_container_width=True)

selected_months = [prior, month] if compare else [month]
st.markdown('<div class="kicker">Performance / '+section+'</div>', unsafe_allow_html=True)
st.title("Monthly performance" if section == "Overview" else section)
st.caption(month_name(month) + (f"  ·  compared with {month_name(prior)}" if compare else "  ·  monthly snapshot"))

def row(platform, key, period=None):
    return metric_row(metrics, period or month, platform, key)

def cards(items):
    """Items: platform, metric code, concise label, optional direction."""
    columns = st.columns(len(items))
    for col, item in zip(columns, items):
        platform, key, label, *direction = item
        current = row(platform, key)
        old = row(platform, key, prior) if compare else None
        delta = delta_label(current, old)
        qualifier = str(current.scope)
        if current.unit == "currency_unconfirmed":
            qualifier += " Currency is unconfirmed. Recorded amounts are not verified cash receipts."
        with col:
            st.metric(label, display_value(current), delta, border=True,
                      delta_color=direction[0] if direction else "off", help=qualifier,
                      delta_description=f"Compared with {month_name(prior)}" if compare and delta else None)

def styled_chart(fig, height=320, legend=True):
    fig.update_layout(height=height, margin=dict(l=0,r=10,t=15,b=0), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Arial, sans-serif",color="#343A56",size=12),
                      legend=dict(title="",orientation="h",y=1.14,x=0), showlegend=legend)
    fig.update_xaxes(title=None,showgrid=False)
    fig.update_yaxes(title=None,gridcolor="#E5E5E0",zeroline=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar":False})

def month_bars(frame, x, y, height=320):
    frame=frame.copy()
    frame["Month"]=frame.month.map(month_name)
    fig=px.bar(frame,x=x,y=y,color="Month",barmode="group",text_auto=True,
               color_discrete_map={month_name(month):PINK,month_name(prior):GRAY} if compare else {month_name(month):PINK})
    fig.update_traces(textposition="outside",cliponaxis=False)
    styled_chart(fig,height)

def section_note(text):
    st.caption(text)

def overview():
    cards([("Squarespace","visits","Website visits"),("HoneyBook","lead_records","CRM lead records"),
           ("Squarespace","button_clicks","Website button clicks"),("HoneyBook","recorded_payment_total","Recorded payment amount")])
    if month == "2026-08" and compare:
        st.markdown('<div class="insight"><strong>More visits, fewer website actions.</strong> Visits rose 19.3% to 384, while button clicks fell 36.4% to 14. CRM lead records increased from 5 to 9; their connection to this traffic is unverified.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="insight"><strong>A baseline for the next report.</strong> Explore traffic, content, website actions and recorded business activity. Missing channels remain pending.</div>', unsafe_allow_html=True)
    section_note("Payments: currency unconfirmed. August includes a 450.00 entry flagged as trade. These amounts are not marketing-attributed revenue.")
    left,right=st.columns(2,gap="large")
    with left:
        st.subheader("Where website visits came from")
        source=frames["website_sources"]
        source=source[source.month.isin(selected_months)&(source.level=="channel")]
        month_bars(source,"source","visits")
        section_note("Source categories reported by Squarespace. Direct traffic does not identify a specific campaign.")
    with right:
        st.subheader("Social content views")
        social=metrics[metrics.month.isin(selected_months)&(((metrics.platform=="Facebook")&(metrics.metric=="views"))|((metrics.platform=="Instagram")&(metrics.metric=="views_instagram_only")))]
        month_bars(social,"platform","value")
        section_note("Instagram-only views and Facebook views. These are content views, not unique people.")
    st.subheader("What we can measure")
    a,b,c=st.columns(3)
    with a:
        st.markdown("**Website actions**")
        st.write(f"{display_value(row('Squarespace','button_clicks'))} button clicks and {display_value(row('Squarespace','recorded_form_submissions'))} Squarespace-recorded form submissions.")
        st.caption("External forms and bookings require their own completion data.")
    with b:
        st.markdown("**Visibility Report funnel**")
        st.write(f"{display_value(row('ClickFunnels','report_funnel_views'))} views · {display_value(row('ClickFunnels','report_funnel_unique_views'))} unique views · {display_value(row('ClickFunnels','report_funnel_optins'))} opt-ins")
        st.caption("Only this ClickFunnels funnel is included. Other funnels remain pending.")
    with c:
        st.markdown("**Outcome attribution**")
        st.write("Booked calls, advertising spend and attributed revenue: pending.")
        st.caption("No website-to-lead conversion rate or ROAS is calculated.")

def social():
    platform=st.radio("Platform",["Instagram","Facebook"],horizontal=True,key="social_platform")
    is_ig=platform=="Instagram"
    cards([(platform,"views_instagram_only" if is_ig else "views","Instagram-only views" if is_ig else "Views"),
           (platform,"interactions","Content interactions"),
           (platform,"profile_visits" if is_ig else "visits","Profile visits" if is_ig else "Page visits"),
           (platform,"link_clicks","Link clicks")])
    cards([(platform,"monthly_reach" if is_ig else "monthly_viewers","Monthly reach ≈" if is_ig else "Monthly viewers ≈"),
           (platform,"follows","Follows")])
    st.caption("Monthly reach/viewers are rounded source figures. They are not summed from daily unique counts. Follows are not net follower growth.")
    st.subheader("Daily activity")
    daily=frames["social_daily"]
    daily=daily[(daily.platform==platform)&daily.month.isin(selected_months)].copy()
    labels={"interactions":"Content interactions","link_clicks":"Link clicks","profile_visits":"Profile visits",
            "visits":"Page visits","views":"Views","views_combined":"Views including Facebook",
            "daily_reach":"Daily reach","daily_viewers":"Daily viewers","follows":"Follows"}
    options=list(daily.metric.unique())
    options.sort(key=lambda key:(key!="interactions",labels.get(key,key)))
    key=st.selectbox("Daily measure",options,format_func=lambda key:labels.get(key,key),key=f"daily_{platform}")
    data=daily[daily.metric==key].copy()
    data["Day"]=pd.to_datetime(data.date).dt.day
    data["Month"]=data.month.map(month_name)
    fig=px.line(data,x="Day",y="value",color="Month",markers=False,
                color_discrete_map={month_name(month):PINK,month_name(prior):GRAY} if compare else {month_name(month):PINK})
    fig.update_traces(line_width=2.5)
    styled_chart(fig,350)
    if is_ig and "view" in key:
        st.info("The Instagram daily Views export includes Facebook views. Instagram-only daily views are unavailable; the monthly card above uses the separate Instagram-only total.")
    if key in ["daily_reach","daily_viewers"]:
        st.caption("People may appear on multiple days. Daily unique counts cannot be added to produce a monthly audience.")
    with st.expander("Monthly figures and definitions"):
        table=public_monthly_table(metrics,month)
        st.dataframe(table[table.Platform==platform],hide_index=True,width="stretch")

def website():
    cards([("Squarespace","visits","Visits"),("Squarespace","unique_visitors","Unique visitors"),
           ("Squarespace","pageviews","Pageviews"),("Squarespace","bounce_rate","Bounce rate","inverse")])
    cards([("Squarespace","average_time_on_page_seconds","Average time on page"),("Squarespace","exit_rate","Exit rate","inverse"),
           ("Squarespace","button_clicks","Button clicks"),("Squarespace","recorded_form_submissions","Recorded form submissions")])
    st.caption("Time on page is the reported page average, not session duration. Form counts exclude unverified completions on external services.")
    if month=="2026-08":
        st.caption("Data check pending: August pageviews (360) are below visits (384). Source values are preserved while their definitions are confirmed.")
    left,right=st.columns(2,gap="large")
    with left:
        st.subheader("Traffic sources")
        data=frames["website_sources"]
        month_bars(data[data.month.isin(selected_months)&(data.level=="channel")],"source","visits")
    with right:
        st.subheader("Visits from social platforms")
        data=frames["website_sources"]
        data=data[data.month.isin(selected_months)&(data.level=="social_platform")]
        month_bars(data,"source","visits")
        st.caption("Website referral visits differ from link-click counts in Meta. An unlisted source is not treated as a measured zero.")
    pages=frames["website_pages"]
    pages=pages[pages.month==month].copy()
    st.subheader("Most-viewed pages")
    top=pages.nlargest(10,"views").sort_values("views")
    top["Page"]=top.page_label.map(lambda x:x if len(x)<65 else x[:62]+"…")
    fig=px.bar(top,x="views",y="Page",orientation="h",text="views",color_discrete_sequence=[TEAL])
    fig.update_traces(textposition="outside",cliponaxis=False)
    styled_chart(fig,400,False)
    with st.expander("All viewed pages",expanded=False):
        query=st.text_input("Find a page",key="page_search")
        if query:pages=pages[pages.page_label.str.contains(query,case=False,regex=False)|pages.page_key.str.contains(query,case=False,regex=False)]
        shown=pages[["page_label","views","time_on_page_seconds","bounce_rate","exit_rate"]].copy()
        shown["Time on page"]=shown.time_on_page_seconds.map(lambda x:f"{int(x)//60}:{int(x)%60:02d}")
        for key in ["bounce_rate","exit_rate"]:shown[key]=shown[key].map(lambda x:f"{x:.2%}")
        shown=shown.drop(columns="time_on_page_seconds").rename(columns={"page_label":"Page","views":"Views","bounce_rate":"Bounce rate","exit_rate":"Exit rate"})
        st.dataframe(shown,hide_index=True,width="stretch")
        st.caption("A reported 0:00 is not proof that no reading or engagement occurred.")
    st.subheader("Button actions")
    st.caption("All positive-click placements plus selected zero-click placements. Repeated labels can represent separate buttons.")
    buttons=frames["website_buttons"]
    buttons=buttons[buttons.month==month].sort_values("clicks",ascending=False).copy()
    buttons["Reported conversion rate"]=buttons.conversion_rate_as_reported.map(lambda x:f"{x:.1%}")
    st.dataframe(buttons.rename(columns={"button_label":"Button","placement_key":"Placement","clicks":"Clicks","unique_views_as_reported":"Reported unique views"})[["Button","Placement","Clicks","Reported unique views","Reported conversion rate"]],hide_index=True,width="stretch")
    st.caption("Conversion rates are reproduced as reported. Button clicks are not completed inquiries, opt-ins or booked calls.")

def business():
    st.subheader("Lead records")
    cards([("HoneyBook","lead_records","CRM lead records"),("HoneyBook","unknown_lead_source_records","Unknown source"),
           ("HoneyBook","booked_calls","Booked calls")])
    st.caption("Lead records are not independently qualified leads. Booked calls remain pending; project statuses are not calendar bookings.")
    sources=frames["crm_sources"]
    sources=sources[sources.report_month.isin(selected_months)].rename(columns={"report_month":"month"})
    month_bars(sources,"lead_source","lead_records",300)
    st.divider()
    st.subheader("Recorded payments")
    st.info("Currency is unconfirmed. These are recorded payment amounts, not verified cash receipts or marketing-attributed revenue. August includes a 450.00 entry flagged as trade.")
    cards([("HoneyBook","recorded_payment_total","Recorded amount"),("HoneyBook","recorded_payment_net","Recorded net amount"),
           ("HoneyBook","recorded_payment_fees","Transaction fees"),("HoneyBook","payment_records","Payment records")])
    methods=frames["payment_methods"]
    methods=methods[methods.month.isin(selected_months)].copy()
    month_bars(methods,"payment_method","recorded_amount",300)
    current=methods[methods.month==month].drop(columns="month").rename(columns={"payment_method":"Method","payment_count":"Records","recorded_amount":"Recorded amount","recorded_net_amount":"Recorded net","transaction_fees":"Fees"})
    st.dataframe(current,hide_index=True,width="stretch",column_config={k:st.column_config.NumberColumn(format="%.2f") for k in ["Recorded amount","Recorded net","Fees"]})
    st.caption("Payments are grouped by their recorded payment month. These totals are not a revenue cohort for the leads above.")
    with st.expander("ClickFunnels: Visibility Report only"):
        cards([("ClickFunnels","report_funnel_views","Funnel views"),("ClickFunnels","report_funnel_unique_views","Unique views"),
               ("ClickFunnels","report_funnel_optins","Opt-ins"),("ClickFunnels","report_funnel_thank_you_views","Thank-you views")])
        st.caption("Eastern Time workspace. Other funnels are pending. All-time contact counts and September QA entries are excluded from these monthly figures.")

def coverage():
    st.info("Remaining collection is pending. This draft can be used while access and exports are completed.")
    coverage=pd.DataFrame(meta["coverage"]).rename(columns={"source":"Source","status":"Status","detail":"Coverage"})
    st.dataframe(coverage,hide_index=True,width="stretch",row_height=70)
    st.subheader("How to read this draft")
    st.markdown("""
    - **Zero** means a source recorded zero. **Pending** and **Unavailable** mean no usable figure is present.
    - **Changes** use the July and August values in this dataset, not the platforms’ comparison badges. Rate changes are percentage points.
    - **Audiences** remain separate by platform. Approximate monthly reach/viewers have no exact percentage change.
    - **Attribution** is unverified. Website visits, clicks, CRM leads and payments are separate measures.
    - **Time boundaries** follow the available monthly reports. ClickFunnels uses Eastern Time; other workspace settings still need confirmation.
    - **Refresh** is manual. Figures reflect the supplied exports and screenshots reviewed on 20 September 2026.
    """)
    with st.expander("Current month data dictionary"):
        st.dataframe(public_monthly_table(metrics,month),hide_index=True,width="stretch")
    st.caption("This public app contains aggregate reporting data. Contact records and original exports are excluded.")

{"Overview":overview,"Social":social,"Website":website,"Leads & payments":business,"Data coverage":coverage}[section]()
st.markdown('<div class="foot">PRISMHAUS · Draft monthly reporting · July–August 2026 · Remaining data collection pending</div>', unsafe_allow_html=True)
