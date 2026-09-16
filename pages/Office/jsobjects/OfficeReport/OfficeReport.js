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
