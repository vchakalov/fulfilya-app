export default {
  isAuthenticated: () => {
    return !!(appsmith.store.customer_uuid && appsmith.store.authToken);
  },

  logout: async () => {
    await removeValue('authToken');
    await removeValue('customer_uuid');
    await removeValue('customer_name');
    await removeValue('customer_email');
    await removeValue('is_admin');
    await removeValue('can_change_password');
    await removeValue('pw_result');
    navigateTo('Authentication');
  },

  // The form lives inside BoLoginB, so the email and password arrive as arguments and go to
  // the queries as run() params. Errors are codes the widget words in BG or EN:
  // bad (wrong email or password), nomerchant (signed in, but no merchant behind the login),
  // failed (anything else). Stored for the session only.
  login: async (email, password) => {
    await storeValue('lt_error', '', false);
    try {
      await LtAuth.run({ identity: String(email || '').trim(), password: String(password || '') });
    } catch (e) {
      const code = Number((LtAuth.responseMeta || {}).statusCode || 0);
      await storeValue('lt_error', code >= 400 && code < 500 ? 'bad' : 'failed', false);
      return;
    }
    const data = LtAuth.data || {};
    if (!data.token) {
      await storeValue('lt_error', 'bad', false);
      return;
    }
    try {
      await storeValue('authToken', data.token);

      // A Fulfilya admin has no merchant (contacts) row and is not here to see a
      // merchant's orders - they get the office page.
      if (data.type === 'admin') {
        await storeValue('is_admin', true);
        await storeValue('customer_name', 'Fulfilya');
        navigateTo('Office');
        return;
      }
      await storeValue('is_admin', false);

      await LtCustomer.run({ email: String(email || '').trim() });
      const customer = (LtCustomer.data || [])[0];
      if (!customer) {
        await removeValue('authToken');
        await storeValue('lt_error', 'nomerchant', false);
        return;
      }
      await storeValue('customer_uuid', customer.customer_uuid);
      await storeValue('customer_name', customer.customer_name);
      await storeValue('customer_email', customer.customer_email);
      await storeValue('customer_logo', customer.customer_logo || '');
      await storeValue('can_change_password', ['true', '1'].includes(String(customer.password_change)));
      // Every value above is awaited: the Dashboard reads them the moment it opens.
      navigateTo('Dashboard');
    } catch (e) {
      await storeValue('lt_error', 'failed', false);
    }
  }
}