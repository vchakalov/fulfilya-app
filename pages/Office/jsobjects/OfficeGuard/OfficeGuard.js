export default {
  // Office page: only a Fulfilya admin. The login stores is_admin from the user type the
  // API returns; a merchant who lands here is sent to the login. The report endpoint
  // refuses non-admins with a 403 as well, so this guard is about the door, not the lock.
  protectPage() {
    if (!appsmith.store.is_admin || !appsmith.store.authToken) {
      navigateTo('Authentication');
      return false;
    }
    // The page always opens on this month (Maria, 2026-10-23) - not on whatever period was
    // picked last time, which the store would otherwise remember.
    OfficeReport.setPeriod('month');
    return true;
  }
}
