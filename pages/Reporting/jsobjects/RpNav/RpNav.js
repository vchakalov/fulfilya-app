export default {
  tz: () => moment().tz('Europe/Sofia').utcOffset() / 60,
  today: () => moment().tz('Europe/Sofia').format('YYYY-MM-DD'),
  period: () => appsmith.store.rp_period || 'month',
  // today | Monday-Sunday week | calendar month | range - Sofia dates, inclusive
  since: () => {
    const p = RpNav.period();
    const now = moment().tz('Europe/Sofia');
    if (p === 'today') return now.format('YYYY-MM-DD');
    if (p === 'week') return now.startOf('isoWeek').format('YYYY-MM-DD');
    if (p === 'range' && appsmith.store.rp_from) return appsmith.store.rp_from;
    return now.startOf('month').format('YYYY-MM-DD');
  },
  until: () => {
    const p = RpNav.period();
    const now = moment().tz('Europe/Sofia');
    if (p === 'today') return now.format('YYYY-MM-DD');
    if (p === 'week') return now.endOf('isoWeek').format('YYYY-MM-DD');
    if (p === 'range' && appsmith.store.rp_to) return appsmith.store.rp_to;
    return now.endOf('month').format('YYYY-MM-DD');
  },
  monthsSince: () => moment().tz('Europe/Sofia').subtract(5, 'months').startOf('month').format('YYYY-MM-DD'),

  reload: async () => {
    await Promise.all([RpStats.run(), RpPayment.run(), RpService.run(), RpOutcome.run(), RpProducts.run(), RpDaily.run()]);
  },
  setPeriod: async (p) => {
    await storeValue('rp_period', p);
    await RpNav.reload();
  },
  setRange: async (from, to) => {
    await storeValue('rp_from', from);
    await storeValue('rp_to', to);
    await storeValue('rp_period', 'range');
    await RpNav.reload();
  },

  // The daily table as a CSV the merchant's accountant can open. Excel in Bulgaria reads a
  // semicolon-separated file with a BOM as columns straight away; a comma-separated one
  // lands in a single column.
  exportCsv: () => {
    const rows = RpDaily.data || [];
    const head = ['Ден', 'Доставени', 'Върнати', 'НП в брой', 'НП с карта', 'Платени онлайн', 'Общо събрано', 'Доставка и такса НП', 'За изплащане'];
    const cell = (v) => String(v == null ? '' : v).replace('.', ',');
    const lines = [head.join(';')].concat(rows.map((r) => [r.day, r.delivered, r.returned, cell(r.cod_cash), cell(r.cod_card), cell(r.prepaid), cell(r.collected), cell(r.fees), cell(r.payout)].join(';')));
    download('﻿' + lines.join('\r\n'), `fulfilya-otchet-${RpNav.since()}-${RpNav.until()}.csv`, 'text/csv');
  },

  onHeader: async () => {
    const m = BoHeader.model || {};
    if (m.action === 'logout') return AuthManager.logout();
    if (m.action === 'new') return navigateTo('Dashboard', { new: '1' });
    if (m.action === 'nav' && m.page) return navigateTo(m.page);
  },
  onReports: async () => {
    const m = BoReports.model || {};
    if (m.action === 'period' && m.period) return RpNav.setPeriod(m.period);
    if (m.action === 'range' && m.from && m.to) return RpNav.setRange(m.from, m.to);
    if (m.action === 'csv') return RpNav.exportCsv();
  }
}
