# BackOffice generators

The Fulfilya BackOffice pages (Табло, Справки, Поръчки view, Office header) are hand-authored
Appsmith export files produced by these scripts — edit the script, rerun, rsync `bo-build*/pages/`
over `pages/`, commit, and Ico pulls in the Appsmith editor (Discard & pull) and deploys.

- `bo-build.py` — Dashboard: BoHeader + BoTablo custom widgets, Bo* queries, BoNav, the
  relabelled OrdersTable, the merchant-logo lookup at login.
  Also the **товарителница** (TODO 42, 2026-10-01): a "Генерирай товарителница" button column
  on OrdersTable, and in BoTitle the paper size (`appsmith.store.wb_size`, label | a4) plus
  "Принтирай всички чакащи". Both run the WaybillPDF query (`int/v1/portal/waybills`, merchant
  token, pdf-base64) through `wb_js()` and hand the bytes to `download()`.
- `bo-build-reports.py` — Reporting: header + BoReports, Rp* queries, RpNav; imports the header
  from bo-build.py.
- `bo-build-payouts.py` — **Изплащания** (Payouts), a whole page of its own: the page manifest,
  header, BoPayouts widget, PoLines, and per-page copies of AuthManager/PageGuard (JS objects do
  not cross pages). A new page also needs its entry in `application.json`.
- `bo-build-import.py` — **Качи поръчки** (Import, 2026-09-30), a page of its own like Изплащания: the
  merchant uploads an Excel/CSV order export, checks the rows, and each chosen row is created through
  `POST int/v1/portal/orders` (the ImportOrder query, run one at a time by the ImportJS object). All
  of the file reading is `import-parse.js`, inlined into the widget and tested with
  `node import-parse.test.js` — add a shop's column names to its `FIELDS` when a new export arrives.
  Relies on the backend's duplicate guard (409 `duplicate`) so the same file uploaded twice creates nothing twice.
- `bo-build-office.py` — Office header, shifts the Office widgets, switches Appsmith's navbar off.

`bo_i18n.py` is shared: every widget embeds the whole dictionary, so adding one phrase rewrites
**every** widget JSON. That is expected — rerun all the generators together, never one alone.

Paths resolve from the script's own folder (fixed 2026-09-19; they used to point at the
scratchpad of the session that wrote them, so a rerun could silently revert later changes).
`mark.b64` is the wing mark embedded in the header. The scripts reuse the repo's existing gitSyncIds — never regenerate those, Appsmith
would import a query twice.
