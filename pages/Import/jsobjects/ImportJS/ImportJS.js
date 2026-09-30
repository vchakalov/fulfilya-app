export default {
  async createAll(orders, batch) {
    const list = Array.isArray(orders) ? orders : [];
    const items = {};
    const put = (running) => storeValue('imp_results', { batch: batch, items: Object.assign({}, items), running: running, total: list.length });
    await put(true);
    for (const o of list) {
      try {
        const r = await ImportOrder.run({ order: o.body });
        items[o.key] = { ok: true, order_id: (r && r.order_id) || '' };
      } catch (e) {
        // A refused order is an answer, not a crash: the server's reason is in .data.
        const b = ImportOrder.data || {};
        items[o.key] = b.duplicate
          ? { dup: true, order_id: b.order_id || '' }
          : { error: String(b.error || (e && e.message) || '') };
      }
      await put(true);
    }
    await put(false);
    return items;
  }
}
