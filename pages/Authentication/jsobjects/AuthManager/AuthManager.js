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
        storeValue('authToken', FleetbaseAuth.data.token);

        // A Fulfilya admin has no merchant (contacts) row and is not here to see a
        // merchant's orders - they get the office page. The API says who is who: the
        // login answer carries the user's type ('admin' for the office account).
        if (FleetbaseAuth.data?.type === 'admin') {
          storeValue('is_admin', true);
          storeValue('customer_name', 'Fulfilya');
          navigateTo('Office');
          return;
        }
        storeValue('is_admin', false);

        // Get customer data
        await GetCustomerByEmail.run();
        
        if (GetCustomerByEmail.data?.length > 0) {
          const customer = GetCustomerByEmail.data[0];
          
          // Store customer data
          storeValue('customer_uuid', customer.customer_uuid);
          storeValue('customer_name', customer.customer_name);
          storeValue('customer_email', customer.customer_email);
          // The merchant's logo: the photo on their Contact in the console, if one was uploaded.
          storeValue('customer_logo', customer.customer_logo || '');
          
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