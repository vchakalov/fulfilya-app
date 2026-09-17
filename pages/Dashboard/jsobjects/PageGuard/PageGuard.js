export default {
    protectPage() {
      if (!AuthManager.isAuthenticated()) {
        navigateTo('Authentication');
        return false;
      }
      // "Нова поръчка" from another page's header lands here with ?new=1 and opens the form.
      if (appsmith.URL.queryParams && appsmith.URL.queryParams.new === '1') {
        showModal('CreateOrderModal');
      }
      return true;
    }
  }