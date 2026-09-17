# BackOffice generators

The Fulfilya BackOffice pages (Табло, Справки, Поръчки view, Office header) are hand-authored
Appsmith export files produced by these scripts — edit the script, rerun, rsync `bo-build*/pages/`
over `pages/`, commit, and Ico pulls in the Appsmith editor (Discard & pull) and deploys.

- `bo-build.py` — Dashboard: BoHeader + BoTablo custom widgets, Bo* queries, BoNav, the
  relabelled OrdersTable, the merchant-logo lookup at login.
- `bo-build-reports.py` — Reporting: header + BoReports, Rp* queries, RpNav; imports the header
  from bo-build.py.
- `bo-build-office.py` — Office header, shifts the Office widgets, switches Appsmith's navbar off.

Paths inside the scripts point at the session scratchpad they were written in (2026-09-17);
change `S`/`OUT` to a local folder before running. `mark.b64` is the wing mark embedded in the
header. The scripts reuse the repo's existing gitSyncIds — never regenerate those, Appsmith
would import a query twice.
