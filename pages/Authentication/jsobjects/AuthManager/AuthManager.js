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
        
        // Get customer data
        await GetCustomerByEmail.run();
        
        if (GetCustomerByEmail.data?.length > 0) {
          const customer = GetCustomerByEmail.data[0];
          
          // Store customer data
          storeValue('customer_uuid', customer.customer_uuid);
          storeValue('customer_name', customer.customer_name);
          storeValue('customer_email', customer.customer_email);
          
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