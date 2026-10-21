export default {
    protectPage() {
      if (!AuthManager.isAuthenticated()) {
        navigateTo('Authentication');
        return false;
      }
      // The header must show whoever is signed in NOW. After Изход and a login as another merchant
      // it kept the model of the last click (blank name, "F" avatar) until a refresh (2026-10-22),
      // so every page puts it back to its default model when it opens.
      resetWidget('BoHeader', true);
      return true;
    }
  }