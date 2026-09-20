# Public data dictionary

All monthly keys use `YYYY-MM`. The July/August dataset is a historical snapshot; no live credentials or automatic refresh are configured. Public files intentionally omit names, email addresses, account IDs, contact records, payment IDs, original screenshots, and raw exports.

| File | Grain | Key definitions |
| --- | --- | --- |
| `metrics.csv` | Month × platform × metric | `value` is numeric or blank; `unit`, `data_status`, `precision`, `aggregation`, and `scope` define interpretation. `dashboard_default` controls the monthly download/dictionary. |
| `social_daily.csv` | Day × platform × metric | Daily counts. `aggregation_to_month=sum` for additive activity; unique daily reach/viewers cannot supply monthly unique totals. Instagram `views_combined` includes Facebook. |
| `website_sources.csv` | Month × level × source | `channel` categories sum to total visits. `social_platform` is a breakdown of Social and must not be added to the channel totals. Unlisted sources are missing, not imputed zero. |
| `website_pages.csv` | Month × page | Views, reported time in seconds, and bounce/exit rates as proportions. Contains all pages with views in the supplied tables. |
| `website_buttons.csv` | Month × placement | Click counts and source-reported unique views/conversion rate. Inventory includes all positive-click placements plus selected zero-click placements. Separate placements may share a label. |
| `crm_sources.csv` | Month × lead source | Counts of HoneyBook lead records; unknown attribution stays Unknown. |
| `payment_methods.csv` | Month × payment method | Counts, recorded gross/net amounts, and transaction fees. No payer or transaction identifiers. Currency remains unconfirmed. |
| `metadata.json` | Dataset | Available months, snapshot date, currency/collection status, refresh mode, and public coverage notes. |

## Missingness and precision

`observed` means reproduced from supplied evidence, not independently audited. `rounded` values use the approximate symbol and receive no exact delta. `provisional` values need interpretation confirmed. `unavailable`, `pending_access`, `pending_collection`, and `pending_confirmation` have blank numeric values.

Rates are stored as fractions: `0.8534` means 85.34%. Differences between rates are percentage points. Count/amount differences use `(current − previous) / previous`; a previous zero is described without division. No prior-month delta appears when the prior month is absent.

## Scope limits

The app uses `Instagram/views_instagram_only` for monthly views. `views_combined` and its Facebook component are retained only as reconciliation evidence. They must not be added to Facebook's own Views metric.

Monthly reach/viewers are rounded screenshot values. Daily reach/viewers may count the same person on multiple dates. Follows are not net follower growth.

Website engagement values preserve the source, including August's 360 pageviews versus 384 visits. Platform definitions and timezone boundaries need confirmation. The app recomputes July-to-August changes rather than reusing the source's comparison badges.

HoneyBook lead records are not qualified or linked to website visits. Payments are grouped by payment month, not by the lead-creation cohort. A 450.00 August manual entry is flagged as trade. Project-export booking states are not confirmed calls or a complete monthly booking count and are not promoted to headline outcomes.

ClickFunnels figures represent the Visibility Report funnel only, using the workspace's Eastern Time date boundaries. September QA activity and all-time workspace contact counts are excluded from monthly funnel cards.
