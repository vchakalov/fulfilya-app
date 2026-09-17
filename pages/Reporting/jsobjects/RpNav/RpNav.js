export default {
  // Pure on purpose - see BoNav on the Dashboard: a reference to a widget or a query in
  // here closes a dependency loop and nothing runs on page load.
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
  monthsSince: () => moment().tz('Europe/Sofia').subtract(5, 'months').startOf('month').format('YYYY-MM-DD')
}
