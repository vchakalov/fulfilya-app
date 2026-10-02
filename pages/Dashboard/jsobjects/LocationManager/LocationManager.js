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
      showAlert("Адресът е извън България — въведете адрес в София", "warning");
      return;
    }

    // The merchant's own words stay in the field; the search only places the pin.
    // Overwriting them with Google's formatted line lost the housing complex on every
    // ж.к. address: "ж.к. Младост 1, бл. 15" came back as "Bl. 15, Mladost 1Mladost, ..."
    // and the order was stored as "Bl. 15" (found in testing, 2026-10-01). The server
    // geocodes this same text again when the order is created.
    NewPickupLatHidden.setValue(loc.lat);
    NewPickupLngHidden.setValue(loc.lng);
    // The text this pin belongs to. The field's text-change handler runs a moment after
    // the last keystroke, so on a quick type-and-search it could land AFTER this and wipe
    // the pin it had just been given - "found", then "още не е намерен" on Създай (2026-10-02).
    storeValue("newPickupSearchedText", (NewPickupAddressInput.text || "").trim(), false);

    showAlert("✓ Адресът за взимане е намерен на картата", "success");
  } else {
    showAlert("Адресът не е намерен — проверете изписването", "warning");
  }
},

updateNewDropoffFromGeocode: () => {
  const geoResult = GeocodeNewDropoffAddress.data?.results?.[0];
  const loc = geoResult?.geometry?.location;
  if (loc && loc.lat && loc.lng) {
    // Validate coordinates are in Bulgaria
    if (!LocationManager.validateCoordinates(loc.lat, loc.lng)) {
      showAlert("Адресът е извън България — въведете адрес в София", "warning");
      return;
    }

    // Google answers an address it cannot read with the whole country or the whole city -
    // "asdfgh qwerty" came back as "found", pinned near Shipka (tester finding, 2026-10-02).
    // Only a street, a building or a neighbourhood counts, and only in and around Sofia;
    // the server applies the same two rules when the order is created.
    const coarse = ["country", "administrative_area_level_1", "administrative_area_level_2",
      "administrative_area_level_3", "colloquial_area", "political", "locality", "postal_code", "postal_town"];
    const types = geoResult.types || [];
    const onlyTown = types.length > 0 && types.every((t) => coarse.includes(t));
    const inSofia = loc.lat >= 42.55 && loc.lat <= 42.86 && loc.lng >= 23.10 && loc.lng <= 23.62;
    if (onlyTown || !inSofia) {
      NewDropoffLatHidden.setValue("");
      NewDropoffLngHidden.setValue("");
      showAlert("Адресът не е намерен в София — проверете улицата и номера (напр. ул. Витоша 15, София)", "warning");
      return;
    }

    // The merchant's own words stay in the field; the search only places the pin.
    // Overwriting them with Google's formatted line lost the housing complex on every
    // ж.к. address: "ж.к. Младост 1, бл. 15" came back as "Bl. 15, Mladost 1Mladost, ..."
    // and the order was stored as "Bl. 15" (found in testing, 2026-10-01). The server
    // geocodes this same text again when the order is created.
    NewDropoffLatHidden.setValue(loc.lat);
    NewDropoffLngHidden.setValue(loc.lng);
    // The text this pin belongs to. The field's text-change handler runs a moment after
    // the last keystroke, so on a quick type-and-search it could land AFTER this and wipe
    // the pin it had just been given - "found", then "още не е намерен" on Създай (2026-10-02).
    storeValue("newDropoffSearchedText", (NewDropoffAddressInput.text || "").trim(), false);

    showAlert("✓ Адресът за доставка е намерен на картата", "success");
  } else {
    showAlert("Адресът не е намерен — проверете изписването", "warning");
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
    // The next order's pickup is the warehouse again, coordinates and all (2026-10-01).
    const w = (BoWarehouse.data || [])[0];
    if (w && w.address) {
      NewPickupAddressInput.setValue(w.address).then(() => {
        NewPickupLatHidden.setValue(String(w.lat));
        NewPickupLngHidden.setValue(String(w.lng));
      });
    } else {
      NewPickupAddressInput.setValue('');
      NewPickupLatHidden.setValue('');
      NewPickupLngHidden.setValue('');
    }
    NewDropoffAddressInput.setValue('');
    NewDropoffLatHidden.setValue('');
    NewDropoffLngHidden.setValue('');
    ItemNameInput.setValue('');
    ItemSkuInput.setValue('');
    ItemQuantityInput.setValue('1');
    DeliveryNotesInput.setValue('');
    CustomerEmailInput.setValue('');
    // The recipient, added 2026-09-19. Without these two the next order opens carrying
    // the last customer's name and phone, which is how a parcel gets rung through to the
    // wrong person.
    RecipientNameInput.setValue('');
    RecipientPhoneInput.setValue('');
    NewAmountInput.setValue('');
    storeValue('newOrderItems', []);

    // Reset selects to defaults
    NewPaymentMethodSelect.setSelectedOption('COD');
  }
  }
