# Review data dictionary

All monthly keys use `YYYY-MM`. The July/August dataset is a historical snapshot; no live data integrations or automatic refresh are configured. Login credentials are kept separately in private Streamlit Secrets. Public files intentionally omit names, email addresses, account IDs, contact records, payment IDs, original screenshots, and raw exports.

| File | Grain | Key definitions |
| --- | --- | --- |
| `metrics.csv` | Month × platform × metric | `value` is numeric or blank; `unit`, `data_status`, `precision`, `aggregation`, and `scope` define interpretation. `dashboard_default` controls the monthly download/dictionary. |
| `social_daily.csv` | Day × platform × metric | Daily counts. `aggregation_to_month=sum` for additive activity; unique daily reach/viewers cannot supply monthly unique totals. Instagram `views_combined` includes Facebook. |
| `website_sources.csv` | Month × level × source | `channel` categories sum to total visits. `social_platform` is a breakdown of Social and must not be added to the channel totals. Unlisted sources are missing, not imputed zero. |
| `website_pages.csv` | Month × page | Views, reported time in seconds, and bounce/exit rates as proportions. Contains all pages with views in the supplied tables. |
| `website_buttons.csv` | Month × placement | Click counts and source-reported unique views/conversion rate. Inventory includes all positive-click placements plus selected zero-click placements. Separate placements may share a label. |
| `crm_sources.csv` | Month × lead source | Synthetic HoneyBook lead-source counts; each source is labelled demo. |
| `payment_methods.csv` | Month × payment method | Synthetic payment counts, gross/net amounts and transaction fees in USD. No real payer or transaction information. |
| `metadata.json` | Dataset | Available months, snapshot date, currency/collection status, refresh mode, and public coverage notes. |

## Missingness and precision

`synthetic` means an independent HoneyBook illustration, not an observation. Every nonblank HoneyBook value has this status and an illustrative scope label. Pending HoneyBook values remain blank.

`observed` means reproduced from supplied evidence, not independently audited. `rounded` values use the approximate symbol and receive no exact delta. `provisional` values need interpretation confirmed. `unavailable`, `pending_access`, `pending_collection`, and `pending_confirmation` have blank numeric values.

Rates are stored as fractions: `0.8534` means 85.34%. Differences between rates are percentage points. Count/amount differences use `(current − previous) / previous`; a previous zero is described without division. No prior-month delta appears when the prior month is absent.

## Scope limits

The app uses `Instagram/views_instagram_only` for monthly views. `views_combined` and its Facebook component are retained only as reconciliation evidence. They must not be added to Facebook's own Views metric.

Monthly reach/viewers are rounded screenshot values. Daily reach/viewers may count the same person on multiple dates. Follows are not net follower growth.

Website engagement values preserve the source, including August's 360 pageviews versus 384 visits. Platform definitions and timezone boundaries need confirmation. The app recomputes July-to-August changes rather than reusing the source's comparison badges.

HoneyBook leads and payments are fictional and cannot be linked to actual website visits. Synthetic gross amounts equal net amounts plus fees, and source/method breakdowns reconcile. The independent fixture is defined in `synthetic_honeybook.py`; every HoneyBook row is validated against it. Booked calls, complete booked-project counts and attributed revenue remain pending. No real HoneyBook values or business-specific payment notes are retained.

ClickFunnels figures represent the Visibility Report funnel only, using the workspace's Eastern Time date boundaries. September QA activity and all-time workspace contact counts are excluded from monthly funnel cards.
