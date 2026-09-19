export default {
    // Validate coordinates are within Bulgaria bounds
    validateCoordinates: (lat, lng) => {
      const latNum = parseFloat(lat);
      const lngNum = parseFloat(lng);

      // Bulgaria bounds: approximately 41.2-44.2 N, 22.4-28.6 E
      return latNum >= 41.2 && latNum <= 44.2 &&
             lngNum >= 22.4 && lngNum <= 28.6;
    },

    // Extract resolved address from a Google Geocoding API result
    getResolvedAddress: (geoResult) => {
      const fullAddress = geoResult.formatted_address || '';

      const components = geoResult.address_components || [];
      const getComponent = (type) => {
        const match = components.find(c => c.types.includes(type));
        return match ? match.long_name : null;
      };

      const structured = [
        getComponent('street_number'),
        getComponent('route'),
        getComponent('neighborhood') || getComponent('sublocality'),
        getComponent('locality'),
        getComponent('administrative_area_level_1'),
        getComponent('postal_code'),
        getComponent('country')
      ].filter(Boolean).join(', ');

      return {
        fullAddress: fullAddress,
        structured: structured,
        shortName: getComponent('route') || getComponent('neighborhood') || fullAddress.split(',')[0]
      };
    },
  updatePickupFromGeocode: () => {
      const geoResult = GeocodePickupAddress.data?.results?.[0];
      const loc = geoResult?.geometry?.location;
      if (loc && loc.lat && loc.lng) {
        // Validate coordinates are in Bulgaria
        if (!LocationManager.validateCoordinates(loc.lat, loc.lng)) {
          showAlert("Location found outside Bulgaria - keeping current location", "warning");
          return;
        }

        // Get fully resolved address from API response
        const resolvedAddress = LocationManager.getResolvedAddress(geoResult);

        // Update address input with resolved address
        PickupAddressInput.setValue(resolvedAddress.fullAddress);

        // Update hidden coordinate fields
        PickupLatHidden.setValue(loc.lat);
        PickupLngHidden.setValue(loc.lng);

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
    const geoResult = GeocodeDropoffAddress.data?.results?.[0];
    const loc = geoResult?.geometry?.location;

    if (loc && loc.lat && loc.lng) {
      // Validate coordinates are in Bulgaria
      if (!LocationManager.validateCoordinates(loc.lat, loc.lng)) {
        showAlert("Location found outside Bulgaria - keeping current location", "warning");
        return;
      }

      // Get fully resolved address from API response
      const resolvedAddress = LocationManager.getResolvedAddress(geoResult);

      // Update address input with resolved address
      DropoffAddressInput.setValue(resolvedAddress.fullAddress);

      // Update hidden coordinate fields
      DropoffLatHidden.setValue(loc.lat);
      DropoffLngHidden.setValue(loc.lng);

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
  const geoResult = GeocodeNewPickupAddress.data?.results?.[0];
  const loc = geoResult?.geometry?.location;
  if (loc && loc.lat && loc.lng) {
    // Validate coordinates are in Bulgaria
    if (!LocationManager.validateCoordinates(loc.lat, loc.lng)) {
      showAlert("Location found outside Bulgaria - please enter a Bulgarian address", "warning");
      return;
    }

    // Get fully resolved address from API response
    const resolvedAddress = LocationManager.getResolvedAddress(geoResult);

    // Update address input with resolved address
    NewPickupAddressInput.setValue(resolvedAddress.fullAddress);

    // Update hidden coordinate fields
    NewPickupLatHidden.setValue(loc.lat);
    NewPickupLngHidden.setValue(loc.lng);

    showAlert(`Pickup location found: ${resolvedAddress.shortName}`, "success");
  } else {
    showAlert("Address not found - please check spelling", "warning");
  }
},

updateNewDropoffFromGeocode: () => {
  const geoResult = GeocodeNewDropoffAddress.data?.results?.[0];
  const loc = geoResult?.geometry?.location;
  if (loc && loc.lat && loc.lng) {
    // Validate coordinates are in Bulgaria
    if (!LocationManager.validateCoordinates(loc.lat, loc.lng)) {
      showAlert("Location found outside Bulgaria - please enter a Bulgarian address", "warning");
      return;
    }

    // Get fully resolved address from API response
    const resolvedAddress = LocationManager.getResolvedAddress(geoResult);

    // Update address input with resolved address
    NewDropoffAddressInput.setValue(resolvedAddress.fullAddress);

    // Update hidden coordinate fields
    NewDropoffLatHidden.setValue(loc.lat);
    NewDropoffLngHidden.setValue(loc.lng);

    showAlert(`Delivery location found: ${resolvedAddress.shortName}`, "success");
  } else {
    showAlert("Address not found - please check spelling", "warning");
  }
},

  validateOrderForm: () => {
    const errors = [];

    // Check required fields
    if (!NewPickupAddressInput.text) {
      errors.push("Адресът за взимане е задължителен");
    }

    if (!NewDropoffAddressInput.text) {
      errors.push("Адресът за доставка е задължителен");
    }

    if (!ScheduledDeliveryPicker.selectedDate) {
      errors.push("Датата и часът на доставка са задължителни");
    }

    // Check geocoding with Bulgaria validation
    if (!NewPickupLatHidden.text || !NewPickupLngHidden.text) {
      errors.push("Адресът за взимане още не е намерен — изчакайте или проверете изписването");
    } else if (!LocationManager.validateCoordinates(NewPickupLatHidden.text, NewPickupLngHidden.text)) {
      errors.push("Адресът за взимане трябва да е в България");
    }

    if (!NewDropoffLatHidden.text || !NewDropoffLngHidden.text) {
      errors.push("Адресът за доставка още не е намерен — изчакайте или проверете изписването");
    } else if (!LocationManager.validateCoordinates(NewDropoffLatHidden.text, NewDropoffLngHidden.text)) {
      errors.push("Адресът за доставка трябва да е в България");
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
    CustomerEmailInput.setValue('');
    // The recipient, added 2026-09-19. Without these two the next order opens carrying
    // the last customer's name and phone, which is how a parcel gets rung through to the
    // wrong person.
    RecipientNameInput.setValue('');
    RecipientPhoneInput.setValue('');
    NewAmountInput.setValue('');
    storeValue('newOrderItems', []);

    // Reset selects to defaults
    StoreTypeSelect.setSelectedOption('Shopify');
    NewPaymentMethodSelect.setSelectedOption('COD');
  }
  }
