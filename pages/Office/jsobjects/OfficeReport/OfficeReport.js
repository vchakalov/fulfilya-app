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

  useRange: async () => {
    await storeValue('office_period', 'range');
    await storeValue('office_date', FromDate.formattedDate);
    await storeValue('office_to', ToDate.formattedDate);
    return OfficeReport.run();
  },

  run: async () => {
    if (!appsmith.store.office_period) {
      await storeValue('office_period', 'day');
      await storeValue('office_date', OfficeReport.today());
      await storeValue('office_to', '');
    }
    try {
      await GetCodReport.run();
    } catch (e) {
      const body = GetCodReport.data || {};
      showAlert('Отчетът не можа да се зареди: ' + (body.error || e.message || ''), 'error');
    }
  },

  // Paying the selected merchant everything we owe them. The run covers every delivered
  // order of theirs that no payout has stamped yet - there is no date to pick, because the
  // money is in the account by the time the office presses this (Ico, 2026-09-19). The
  // query itself asks for confirmation first; this only refuses the cases that cannot work.
  payout: async () => {
    const merchant = MerchantSelect.selectedOptionValue;
    if (!merchant || merchant === 'all') {
      showAlert('Избери клиент, на когото изплащаш.', 'warning');
      return;
    }
    const owed = Number(GetPendingPayout.data?.totals?.owed || 0);
    if (!owed) {
      showAlert('Няма неизплатени поръчки за този клиент.', 'info');
      return;
    }
    try {
      await PostPayout.run();
      const r = PostPayout.data || {};
      if (!r.paid) {
        showAlert('Изплащането не мина: ' + (r.error || ''), 'error');
        return;
      }
      await storeValue('last_payout_id', r.payout?.id || '');
      // `net`, never `owed`: the run withholds return charges, so owed is what the
      // orders were worth and net is what actually gets transferred. The toast is the
      // number the office types into the bank, so it has to be the second one.
      const paid = Number(r.totals?.net ?? r.totals?.owed ?? 0);
      const held = Number(r.returns?.totals?.withheld || 0);
      showAlert(
        held
          ? `Изплатени ${paid.toFixed(2)} € по ${r.totals?.orders || 0} поръчки (удържани ${held.toFixed(2)} € за върнати пратки).`
          : `Изплатени ${paid.toFixed(2)} € по ${r.totals?.orders || 0} поръчки.`,
        'success'
      );
      // Both views move: what is still owed, and the report's paid/unpaid split.
      await GetPendingPayout.run();
      await OfficeReport.run();
    } catch (e) {
      const body = PostPayout.data || {};
      showAlert('Изплащането не мина: ' + (body.error || e.message || ''), 'error');
    }
  },

  // The statement for the last payout made on this screen - what goes with the transfer.
  payoutPdf: async () => {
    if (!appsmith.store.last_payout_id) {
      showAlert('Няма изплащане за разписка — първо направи изплащане.', 'warning');
      return;
    }
    try {
      await GetPayoutPdf.run();
      const f = GetPayoutPdf.data || {};
      if (!f.base64) { showAlert('Разписката не дойде от сървъра.', 'error'); return; }
      await download('data:application/pdf;base64,' + f.base64, f.filename || 'izplashtane.pdf', 'application/pdf');
    } catch (e) {
      const body = GetPayoutPdf.data || {};
      showAlert('Разписката не можа да се създаде: ' + (body.error || e.message || ''), 'error');
    }
  },

  downloadPdf: async () => {
    try {
      await GetCodReportPdf.run();
      const f = GetCodReportPdf.data || {};
      if (!f.base64) { showAlert('PDF файлът не дойде от сървъра.', 'error'); return; }
      await download('data:application/pdf;base64,' + f.base64, f.filename || 'nalozhen-platezh.pdf', 'application/pdf');
    } catch (e) {
      const body = GetCodReportPdf.data || {};
      showAlert('PDF файлът не можа да се създаде: ' + (body.error || e.message || ''), 'error');
    }
  }
}
