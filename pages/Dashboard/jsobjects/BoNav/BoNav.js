export default {
  // Sofia time, whatever the browser is set to. The SQL shifts created_at by this many
  // hours before taking the date, so "today" and "this week" are Sofia days.
  tz: () => moment().tz('Europe/Sofia').utcOffset() / 60,
  today: () => moment().tz('Europe/Sofia').format('YYYY-MM-DD'),
  period: () => appsmith.store.bo_period || 'week',
  since: () => {
    const p = BoNav.period();
    const now = moment().tz('Europe/Sofia');
    if (p === 'today') return now.format('YYYY-MM-DD');
    if (p === 'month') return now.startOf('month').format('YYYY-MM-DD');
    return now.subtract(6, 'days').format('YYYY-MM-DD');
  },
  daysSince: () => moment().tz('Europe/Sofia').subtract(13, 'days').format('YYYY-MM-DD'),

  setPeriod: async (p) => {
    await storeValue('bo_period', p);
    await Promise.all([BoStats.run(), BoPayment.run(), BoStatus.run()]);
  },

  // The header and the Табло block are custom widgets: they write what happened into
  // their model and raise one event, and this reads it back.
  onHeader: async () => {
    const m = BoHeader.model || {};
    if (m.action === 'logout') return AuthManager.logout();
    if (m.action === 'new') return showModal('CreateOrderModal');
    if (m.action === 'nav' && m.page) return navigateTo(m.page);
  },
  onTablo: async () => {
    const m = BoTablo.model || {};
    if (m.action === 'period' && m.period) return BoNav.setPeriod(m.period);
    if (m.action === 'new') return showModal('CreateOrderModal');
    if (m.action === 'nav' && m.page) return navigateTo(m.page);
  }
}
