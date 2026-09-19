# BackOffice generators

The Fulfilya BackOffice pages (Табло, Справки, Поръчки view, Office header) are hand-authored
Appsmith export files produced by these scripts — edit the script, rerun, rsync `bo-build*/pages/`
over `pages/`, commit, and Ico pulls in the Appsmith editor (Discard & pull) and deploys.

- `bo-build.py` — Dashboard: BoHeader + BoTablo custom widgets, Bo* queries, BoNav, the
  relabelled OrdersTable, the merchant-logo lookup at login.
- `bo-build-reports.py` — Reporting: header + BoReports, Rp* queries, RpNav; imports the header
  from bo-build.py.
- `bo-build-payouts.py` — **Изплащания** (Payouts), a whole page of its own: the page manifest,
  header, BoPayouts widget, PoLines, and per-page copies of AuthManager/PageGuard (JS objects do
  not cross pages). A new page also needs its entry in `application.json`.
- `bo-build-office.py` — Office header, shifts the Office widgets, switches Appsmith's navbar off.

`bo_i18n.py` is shared: every widget embeds the whole dictionary, so adding one phrase rewrites
**every** widget JSON. That is expected — rerun all four generators together, never one alone.

Paths resolve from the script's own folder (fixed 2026-09-19; they used to point at the
scratchpad of the session that wrote them, so a rerun could silently revert later changes).
`mark.b64` is the wing mark embedded in the header. The scripts reuse the repo's existing gitSyncIds — never regenerate those, Appsmith
would import a query twice.
