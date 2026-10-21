export default {
    protectPage() {
      if (!AuthManager.isAuthenticated()) {
        navigateTo('Authentication');
        return false;
      }
      // "Нова поръчка" from another page's header lands here with ?new=1 and opens the form.
      if (appsmith.URL.queryParams && appsmith.URL.queryParams.new === '1') {
        LocationManager.openNewOrder();
      }
      // "Смяна на парола" from another page's header lands here with ?account=1 (2026-10-21).
      if (appsmith.URL.queryParams && appsmith.URL.queryParams.account === '1' && appsmith.store.can_change_password === true) {
        storeValue('pw_result', { at: Date.now(), reset: true });
        showModal('BoAccountModal');
      }
      return true;
    }
  }