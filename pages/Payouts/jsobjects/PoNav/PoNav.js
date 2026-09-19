export default {
  tz: () => moment().tz('Europe/Sofia').utcOffset() / 60
}
