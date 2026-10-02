export default {
  // The office's Наложен платеж report. The period lives in the store so the two REST
  // queries (GetCodReport / GetCodReportPdf) can read it as URL parameters; the server
  // decides the actual day boundaries (Sofia time, Monday-first weeks, calendar months).
  today: () => moment().tz('Europe/Sofia').format('YYYY-MM-DD'),

  setPeriod: async (kind) => {
    await storeValue('office_period', kind);
    await storeValue('office_date', OfficeReport.today());
    await storeValue('office_to', '');
    return OfficeReport.run();
  },

  // The two dates come from the BoOffice widget now, not from native date pickers - see
  // TODO 37. Called with both or not at all; the handler refuses an incomplete range
  // before it gets here.
  useRange: async (from, to) => {
    await storeValue('office_period', 'range');
    await storeValue('office_date', from || '');
    await storeValue('office_to', to || '');
    return OfficeReport.run();
  },

  run: async () => {
    if (!appsmith.store.office_period) {
      await storeValue('office_period', 'day');
      await storeValue('office_date', OfficeReport.today());
      await storeValue('office_to', '');
    }
    // Messages follow the BG|EN switch (they stayed Bulgarian in English until 2026-10-02).
    // Inline rather than a helper: a new function on this object needs its own metadata entry.
    const en = appsmith.store.bo_lang === 'en';
    try {
      await GetCodReport.run();
    } catch (e) {
      const body = GetCodReport.data || {};
      showAlert((en ? 'The report could not be loaded: ' : 'Отчетът не можа да се зареди: ') + (body.error || e.message || ''), 'error');
    }
  },

  // Paying the selected merchant everything we owe them. The run covers every delivered
  // order of theirs that no payout has stamped yet - there is no date to pick, because the
  // money is in the account by the time the office presses this (Ico, 2026-09-19). The
  // query itself asks for confirmation first; this only refuses the cases that cannot work.
  payout: async () => {
    const en = appsmith.store.bo_lang === 'en';
    const merchant = appsmith.store.office_merchant;
    if (!merchant || merchant === 'all') {
      showAlert(en ? 'Pick the client you are paying.' : 'Избери клиент, на когото изплащаш.', 'warning');
      return;
    }
    const owed = Number(GetPendingPayout.data?.totals?.owed || 0);
    if (!owed) {
      showAlert(en ? 'This client has no unpaid orders.' : 'Няма неизплатени поръчки за този клиент.', 'info');
      return;
    }
    try {
      await PostPayout.run();
      const r = PostPayout.data || {};
      if (!r.paid) {
        showAlert((en ? 'The payout did not go through: ' : 'Изплащането не мина: ') + (r.error || ''), 'error');
        return;
      }
      await storeValue('last_payout_id', r.payout?.id || '');
      // `net`, never `owed`: the run withholds return charges, so owed is what the
      // orders were worth and net is what actually gets transferred. The toast is the
      // number the office types into the bank, so it has to be the second one.
      const paid = Number(r.totals?.net ?? r.totals?.owed ?? 0);
      const held = Number(r.returns?.totals?.withheld || 0);
      const n = r.totals?.orders || 0;
      showAlert(
        en
          ? (held ? `Paid out ${paid.toFixed(2)} € for ${n} orders (${held.toFixed(2)} € withheld for returned parcels).` : `Paid out ${paid.toFixed(2)} € for ${n} orders.`)
          : (held ? `Изплатени ${paid.toFixed(2)} € по ${n} поръчки (удържани ${held.toFixed(2)} € за върнати пратки).` : `Изплатени ${paid.toFixed(2)} € по ${n} поръчки.`),
        'success'
      );
      // Every view moves: what is still owed, the report's paid/unpaid split, and the
      // history - which the payout box reads for its "Разписка от" button, so without it
      // the button kept offering the previous payout's statement (2026-10-02).
      await GetPendingPayout.run();
      await GetPayoutHistory.run();
      await OfficeReport.run();
    } catch (e) {
      const body = PostPayout.data || {};
      showAlert((en ? 'The payout did not go through: ' : 'Изплащането не мина: ') + (body.error || e.message || ''), 'error');
    }
  },

  // The statement for the last payout made on this screen - what goes with the transfer.
  // Either the run just made, or one picked from the history table - the office had no
  // way to reprint an older statement before TODO 37 (the button only ever knew about
  // a payout made in the same browser session).
  payoutPdf: async () => {
    const en = appsmith.store.bo_lang === 'en';
    if (!appsmith.store.receipt_payout_id && !appsmith.store.last_payout_id) {
      showAlert(en ? 'No payout to print a statement for - make a payout first.' : 'Няма изплащане за разписка — първо направи изплащане.', 'warning');
      return;
    }
    try {
      await GetPayoutPdf.run();
      const f = GetPayoutPdf.data || {};
      if (!f.base64) { showAlert(en ? 'The statement did not arrive from the server.' : 'Разписката не дойде от сървъра.', 'error'); return; }
      await download('data:application/pdf;base64,' + f.base64, f.filename || 'izplashtane.pdf', 'application/pdf');
    } catch (e) {
      const body = GetPayoutPdf.data || {};
      showAlert((en ? 'The statement could not be created: ' : 'Разписката не можа да се създаде: ') + (body.error || e.message || ''), 'error');
    }
  },

  downloadPdf: async () => {
    const en = appsmith.store.bo_lang === 'en';
    try {
      await GetCodReportPdf.run();
      const f = GetCodReportPdf.data || {};
      if (!f.base64) { showAlert(en ? 'The PDF did not arrive from the server.' : 'PDF файлът не дойде от сървъра.', 'error'); return; }
      await download('data:application/pdf;base64,' + f.base64, f.filename || 'nalozhen-platezh.pdf', 'application/pdf');
    } catch (e) {
      const body = GetCodReportPdf.data || {};
      showAlert((en ? 'The PDF could not be created: ' : 'PDF файлът не можа да се създаде: ') + (body.error || e.message || ''), 'error');
    }
  }
}
