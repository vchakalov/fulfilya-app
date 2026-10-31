export default {
  // Check if user is authenticated
  isAuthenticated: () => {
    return !!(appsmith.store.customer_uuid && appsmith.store.authToken);
  },
  
  // Handle login
  login: async () => {
    try {
      // Clear previous errors
      storeValue('loginError', '');
      
      // Call Fleetbase API
      await FleetbaseAuth.run();
      
      if (FleetbaseAuth.data?.token) {
        // Store auth token
        await storeValue('authToken', FleetbaseAuth.data.token);

        // A Fulfilya admin has no merchant (contacts) row and is not here to see a
        // merchant's orders - they get the office page. The API says who is who: the
        // login answer carries the user's type ('admin' for the office account).
        if (FleetbaseAuth.data?.type === 'admin') {
          await storeValue('office_view_only', false);
          await storeValue('is_admin', true);
          await storeValue('customer_name', 'Fulfilya');
          navigateTo('Office');
          return;
        }
        await storeValue('is_admin', false);
        await storeValue('office_view_only', false);

        // A "Диспечер" login (2026-10-31) is neither the office account nor a merchant: the server says which
        // (int/v1/portal/me, App\Support\OfficeAccess). It gets the Office page with the money buttons hidden -
        // the server refuses those actions for it anyway. Any failure here just carries on as a merchant login.
        try {
          await OfficeMe.run();
          if (OfficeMe.data?.role === 'dispatcher') {
            await storeValue('is_admin', true);
            await storeValue('office_view_only', true);
            await storeValue('customer_name', 'Fulfilya · Диспечер');
            navigateTo('Office');
            return;
          }
        } catch (e) { /* not the office */ }

        // Get customer data
        await GetCustomerByEmail.run();
        
        if (GetCustomerByEmail.data?.length > 0) {
          const customer = GetCustomerByEmail.data[0];
          
          // Store customer data
          await storeValue('customer_uuid', customer.customer_uuid);
          await storeValue('customer_name', customer.customer_name);
          await storeValue('customer_email', customer.customer_email);
          // The merchant's logo: the photo on their Contact in the console, if one was uploaded.
          await storeValue('customer_logo', customer.customer_logo || '');
          // "Смяна на парола" in the header, for merchants the office switched on (2026-10-21).
          await storeValue('can_change_password', ['true', '1'].includes(String(customer.password_change)));
          
          // Every value above is awaited: the Dashboard reads them the moment it opens, and
          // without the waits it opened with no name and no merchant (0 orders) until a refresh (2026-10-21).
          // Navigate to dashboard
          showAlert(`Welcome ${customer.customer_name}!`, 'success');
          navigateTo('Dashboard');
        } else {
          storeValue('loginError', 'Customer account not found');
        }
      } else {
        storeValue('loginError', 'Invalid credentials');
      }
    } catch (error) {
      storeValue('loginError', 'Login failed. Please try again.');
    }
  }
}