# Validation record

Checked locally on **20 September 2026**, using Python 3.12, Streamlit 1.55.0, pandas 2.2.3, and Plotly 6.5.0.

| Check | Result |
| --- | --- |
| Six unittest groups | Passed |
| Both reporting months across all five sections | Passed, no app exceptions |
| Instagram/Facebook selector and comparison toggle | Passed |
| Instagram daily combined-view warning | Passed |
| July/August sources, pages, buttons, social activity, lead sources and payments reconcile | Passed |
| Pending values remain blank; approximate audiences have no exact delta | Passed |
| Public data contains no email addresses or prohibited person/transaction fields | Passed |
| Local Streamlit health endpoint and application HTML | HTTP 200 |

The interactive checks use Streamlit AppTest. The remote browser cannot reach localhost, so **visual browser review is pending**. GitHub publication and public Streamlit deployment require authenticated browser access; neither is claimed complete by this local validation record.

Reproduce the checks:

```bash
python -m unittest discover -s tests -v
python tools/check_server.py
```
