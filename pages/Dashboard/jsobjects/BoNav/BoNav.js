export default {
  // Sofia time, whatever the browser is set to. The SQL shifts created_at by this many
  // hours before taking the date, so "today" and "this week" are Sofia days.
  //
  // Pure on purpose: nothing here may reference a widget or a query. BoTablo's model
  // depends on BoStats, BoStats depends on these dates - a function in here that read
  // BoTablo.model or called BoStats.run() closed a dependency loop, and Appsmith then
  // evaluated none of it and ran no query on page load (found on the first deploy,
  // 2026-09-17). The clicks are handled in the widgets' own onAction bindings.
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
  daysSince: () => moment().tz('Europe/Sofia').subtract(13, 'days').format('YYYY-MM-DD')
}
