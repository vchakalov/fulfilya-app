export default {
    // Nominatim's parser fails to match many Bulgarian streets when the query
    // includes the "ул./бул./пл./ж.к." type prefix (e.g. "ул. Солунска 2, София"
    // returns zero results, but "Солунска 2, София" resolves correctly).
    // Stripping it before geocoding fixes those false "address not found" cases.
    stripStreetPrefix: (text) => {
      if (!text) return text;
      return text.replace(/^\s*(ул\.?|бул\.?|пл\.?|ж\.?\s?к\.?)\s+/i, '');
    },

    // Validate coordinates are within Bulgaria bounds
    validateCoordinates: (lat, lng) => {
      const latNum = parseFloat(lat);
      const lngNum = parseFloat(lng);

      // Bulgaria bounds: approximately 41.2-44.2 N, 22.4-28.6 E
      return latNum >= 41.2 && latNum <= 44.2 &&
             lngNum >= 22.4 && lngNum <= 28.6;
    },

    // Extract resolved address from Nominatim response
    getResolvedAddress: (geoResult) => {
      // Nominatim returns 'display_name' with full resolved address
      const fullAddress = geoResult.display_name || '';

      // Also build structured address from components if available
      const addr = geoResult.address || {};
      const structured = [
        addr.house_number,
        addr.road || addr.street,
        addr.suburb || addr.neighbourhood,
        addr.city || addr.town || addr.village,
        addr.state || addr.county,
        addr.postcode,
        addr.country
      ].filter(Boolean).join(', ');

      return {
        fullAddress: fullAddress,
        structured: structured,
        shortName: addr.road || addr.suburb || fullAddress.split(',')[0]
      };
    },
  updatePickupFromGeocode: () => {
      const geoResult = GeocodePickupAddress.data?.[0];
      if (geoResult && geoResult.lat && geoResult.lon) {
        // Validate coordinates are in Bulgaria
        if (!LocationManager.validateCoordinates(geoResult.lat, geoResult.lon)) {
          showAlert("Location found outside Bulgaria - keeping current location", "warning");
          return;
        }

        // Get fully resolved address from API response
        const resolvedAddress = LocationManager.getResolvedAddress(geoResult);

        // Update address input with resolved address
        PickupAddressInput.setValue(resolvedAddress.fullAddress);

        // Update hidden coordinate fields
        PickupLatHidden.setValue(geoResult.lat);
        PickupLngHidden.setValue(geoResult.lon);

        // Save to database
        UpdatePickupLocationWithCoords.run().then(() => {
          showAlert(`Pickup location updated: ${resolvedAddress.shortName}`, "success");
          // DON'T refresh GetOrderDetails here - it resets the input!
          // GetOrderDetails.run(); // REMOVE THIS LINE
        }).catch(err => {
          showAlert("Error updating pickup location", "error");
        });
      } else {
        showAlert("Address not found - keeping current location", "warning");
      }
    },
  updateDropoffFromGeocode: () => {
    console.log("updateDropoffFromGeocode called");
    const geoResult = GeocodeDropoffAddress.data?.[0];
    console.log("Geo result:", geoResult);

    if (geoResult && geoResult.lat && geoResult.lon) {
      // Validate coordinates are in Bulgaria
      if (!LocationManager.validateCoordinates(geoResult.lat, geoResult.lon)) {
        showAlert("Location found outside Bulgaria - keeping current location", "warning");
        return;
      }

      // Get fully resolved address from API response
      const resolvedAddress = LocationManager.getResolvedAddress(geoResult);
      console.log("Resolved address:", resolvedAddress);

      // Update address input with resolved address
      DropoffAddressInput.setValue(resolvedAddress.fullAddress);

      // Update hidden coordinate fields
      DropoffLatHidden.setValue(geoResult.lat);
      DropoffLngHidden.setValue(geoResult.lon);

      // Save to database
      UpdateDropoffLocationWithCoord.run().then(() => {
        showAlert(`Delivery location updated: ${resolvedAddress.shortName}`, "success");
      }).catch(err => {
        showAlert("Error updating delivery location", "error");
      });
    } else {
      showAlert("Address not found - keeping current location", "warning");
    }
  },
	updateNewPickupFromGeocode: () => {
  const geoResult = GeocodeNewPickupAddress.data?.[0];
  if (geoResult && geoResult.lat && geoResult.lon) {
    // Validate coordinates are in Bulgaria
    if (!LocationManager.validateCoordinates(geoResult.lat, geoResult.lon)) {
      showAlert("Location found outside Bulgaria - please enter a Bulgarian address", "warning");
      return;
    }

    // Get fully resolved address from API response
    const resolvedAddress = LocationManager.getResolvedAddress(geoResult);

    // Update address input with resolved address
    NewPickupAddressInput.setValue(resolvedAddress.fullAddress);

    // Update hidden coordinate fields
    NewPickupLatHidden.setValue(geoResult.lat);
    NewPickupLngHidden.setValue(geoResult.lon);

    showAlert(`Pickup location found: ${resolvedAddress.shortName}`, "success");
  } else {
    showAlert("Address not found - please check spelling", "warning");
  }
},

updateNewDropoffFromGeocode: () => {
  const geoResult = GeocodeNewDropoffAddress.data?.[0];
  if (geoResult && geoResult.lat && geoResult.lon) {
    // Validate coordinates are in Bulgaria
    if (!LocationManager.validateCoordinates(geoResult.lat, geoResult.lon)) {
      showAlert("Location found outside Bulgaria - please enter a Bulgarian address", "warning");
      return;
    }

    // Get fully resolved address from API response
    const resolvedAddress = LocationManager.getResolvedAddress(geoResult);

    // Update address input with resolved address
    NewDropoffAddressInput.setValue(resolvedAddress.fullAddress);

    // Update hidden coordinate fields
    NewDropoffLatHidden.setValue(geoResult.lat);
    NewDropoffLngHidden.setValue(geoResult.lon);

    showAlert(`Delivery location found: ${resolvedAddress.shortName}`, "success");
  } else {
    showAlert("Address not found - please check spelling", "warning");
  }
},
	
  validateOrderForm: () => {
    const errors = [];
    
    // Check required fields
    if (!NewPickupAddressInput.text) {
      errors.push("Pickup address is required");
    }
    
    if (!NewDropoffAddressInput.text) {
      errors.push("Delivery address is required");
    }
    
    if (!ScheduledDeliveryPicker.selectedDate) {
      errors.push("Scheduled delivery time is required");
    }
    
    // Check geocoding with Bulgaria validation
    if (!NewPickupLatHidden.text || !NewPickupLngHidden.text) {
      errors.push("Pickup address must be geocoded - please wait or check spelling");
    } else if (!LocationManager.validateCoordinates(NewPickupLatHidden.text, NewPickupLngHidden.text)) {
      errors.push("Pickup address must be in Bulgaria");
    }
    
    if (!NewDropoffLatHidden.text || !NewDropoffLngHidden.text) {
      errors.push("Delivery address must be geocoded - please wait or check spelling");
    } else if (!LocationManager.validateCoordinates(NewDropoffLatHidden.text, NewDropoffLngHidden.text)) {
      errors.push("Delivery address must be in Bulgaria");
    }
    
    return {
      isValid: errors.length === 0,
      errors: errors
    };
  },
  
  resetOrderForm: () => {
    // Clear geocoding timeouts
    clearInterval(appsmith.store.newPickupGeoTimeout);
    clearInterval(appsmith.store.newDropoffGeoTimeout);
    
    // Reset all form inputs
    NewPickupAddressInput.setValue('');
    NewDropoffAddressInput.setValue('');
    NewPickupLatHidden.setValue('');
    NewPickupLngHidden.setValue('');
    NewDropoffLatHidden.setValue('');
    NewDropoffLngHidden.setValue('');
    ItemNameInput.setValue('');
    ItemSkuInput.setValue('');
    ItemQuantityInput.setValue('1');
    DeliveryNotesInput.setValue('');
    OrderSourceIdInput.setValue('');
    NewAmountInput.setValue('');
    storeValue('newOrderItems', []);
    
    // Reset selects to defaults
    StoreTypeSelect.setSelectedOption('Shopify');
    NewPaymentMethodSelect.setSelectedOption('COD');
  }
  }