export default {
    protectPage() {
      if (!AuthManager.isAuthenticated()) {
        navigateTo('Authentication');
        return false;
      }
      return true;
    }
  }