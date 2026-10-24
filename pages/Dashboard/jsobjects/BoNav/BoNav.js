export default {
  // Sofia time, whatever the browser is set to. The SQL shifts created_at by this many
  // hours before taking the date, so "today" and "this week" are Sofia days.
  //
  // Pure on purpose: nothing here may name a widget or a query, not even in a comment
  // worth reading twice. The Табло widget's model depends on the stats query, the stats
  // query depends on these dates - a function in here that read the widget's model or
  // ran the query closed a dependency loop, and Appsmith then evaluated none of it and
  // ran no query on page load (found on the first deploy, 2026-09-17). The clicks are
  // handled in the widgets' own onAction bindings.
  tz: () => moment().tz('Europe/Sofia').utcOffset() / 60,
  today: () => moment().tz('Europe/Sofia').format('YYYY-MM-DD'),
  // Месец by default (Maria, 2026-10-24: most merchants do not ship every day, so Днес was zeroes).
  // A new key, kept for the session only: a choice saved under the old one would have won forever.
  period: () => appsmith.store.bo_view_period || 'month',
  since: () => {
    const p = BoNav.period();
    const now = moment().tz('Europe/Sofia');
    if (p === 'today') return now.format('YYYY-MM-DD');
    if (p === 'month') return now.startOf('month').format('YYYY-MM-DD');
    return now.subtract(6, 'days').format('YYYY-MM-DD');
  },
  daysSince: () => moment().tz('Europe/Sofia').subtract(13, 'days').format('YYYY-MM-DD')
}
