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
  // Google's geocoder drops the Cyrillic "бул." (and "ул.", "пл.", "б-р") and then matches
  // the street name anywhere in the country: `бул. сливница 566, софия` came back as a
  // confident street in Кътина, 15 km north, and an order was filed there (2026-10-03,
  // TODO 45). Spelt out, the same text answers the real building in кв. Република. The
  // server does the same before it geocodes the order; the field keeps the merchant's words.
  expandAbbreviations: (text) => {
    const words = { "бул": "булевард", "б-р": "булевард", "ул": "улица", "пл": "площад" };
    const expanded = (text || "").replace(/(?<!\p{L})(бул|б-р|ул|пл)(?:\.|(?=\s))/giu, (m, w) => words[w.toLowerCase()] + " ");
    return expanded.replace(/[ \t]{2,}/g, " ").trim();
  },

  // Cyrillic to Latin the way Google labels Bulgarian towns (Кътина -> Katina, София -> Sofia).
  transliterate: (text) => {
    const map = { а: "a", б: "b", в: "v", г: "g", д: "d", е: "e", ж: "zh", з: "z", и: "i", й: "y", к: "k", л: "l", м: "m",
      н: "n", о: "o", п: "p", р: "r", с: "s", т: "t", у: "u", ф: "f", х: "h", ц: "ts", ч: "ch", ш: "sh", щ: "sht",
      ъ: "a", ь: "y", ю: "yu", я: "ya" };
    const chars = Array.from((text || "").replace(/(ия|ИЯ|Ия)(?!\p{L})/gu, (m) => ({ "ия": "ia", "ИЯ": "IA", "Ия": "Ia" })[m]));
    const isUpper = (c) => c !== undefined && c !== c.toLowerCase();
    return chars.map((c, i) => {
      const lower = c.toLowerCase();
      if (!map[lower]) return c;
      if (c === lower) return map[lower];
      const inCapitals = isUpper(chars[i - 1]) || isUpper(chars[i + 1]);
      const latin = map[lower];
      return inCapitals ? latin.toUpperCase() : latin.charAt(0).toUpperCase() + latin.slice(1);
    }).join("");
  },

  // The town Google put the address in when the typed text never names it (so "с. Бистрица, ..."
  // answered in Bistritsa passes), or "" when the answer is Sofia or names no town at all.
  wrongTown: (geoResult, typed) => {
    const component = (geoResult?.address_components || []).find((c) => (c.types || []).includes("locality"));
    const town = (component?.long_name || "").trim();
    const lower = town.toLowerCase();
    if (!town || lower.includes("sofia") || lower.includes("софия")) return "";
    const written = ((typed || "") + " " + LocationManager.transliterate(typed || "")).toLowerCase();
    return written.includes(lower) ? "" : town;
  },

  // The second try: the same address in Latin, with Sofia named when the text did not name it.
  latinQuery: (typed) => {
    const latin = LocationManager.transliterate(LocationManager.expandAbbreviations(typed));
    return /sofia|софия/i.test(latin) ? latin : latin + ", Sofia";
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
    storeValue("newDropoffSearchedZip", (NewDropoffPostcodeInput.text || "").trim(), false);

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

    // Required since 2026-10-04 (Ico): Google misplaces some streets without it, so every
    // delivery address is searched and created with its postcode.
    if (!/^\d{4}$/.test((NewDropoffPostcodeInput.text || "").trim())) {
      errors.push("Пощенският код на получателя е задължителен (4 цифри, напр. 1000)");
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

  // Opens "Нова поръчка" - the one way in, from the button, the header, the Табло and
  // ?new=1 alike. A draft belongs to one merchant: Appsmith keeps every box's content
  // across a logout and login in the same tab, so after switching accounts the form opened
  // with the PREVIOUS merchant's warehouse as the pickup - TheBasket's form showed
  // Artsyzone's address (2026-10-02). A different merchant gets an empty form and their own
  // warehouse; the same merchant keeps what they typed, as before.
  openNewOrder: async () => {
    const me = appsmith.store.customer_uuid || '';
    if (appsmith.store.newOrderDraftFor !== me) {
      await Promise.all([
        NewPickupAddressInput.setValue(''), NewPickupLatHidden.setValue(''), NewPickupLngHidden.setValue(''),
        NewDropoffAddressInput.setValue(''), NewDropoffPostcodeInput.setValue(''), NewDropoffLatHidden.setValue(''), NewDropoffLngHidden.setValue(''),
        RecipientNameInput.setValue(''), RecipientPhoneInput.setValue(''), CustomerEmailInput.setValue(''),
        DeliveryNotesInput.setValue(''), NewAmountInput.setValue(''),
        ItemNameInput.setValue(''), ItemSkuInput.setValue(''), ItemQuantityInput.setValue('1'),
        ItemWeightInput.setValue(''), ItemLengthInput.setValue(''), ItemWidthInput.setValue(''), ItemHeightInput.setValue(''),
        DeclaredValueInput.setValue('')
      ]);
      DeclaredValueSelect.setSelectedOption('no');
      OrderShippingSelect.setSelectedOption('');
      await storeValue('newOrderDraftFor', me, false);
    }
    storeValue('newOrderItems', []);
    storeValue('newOrderUUIDs', {});
    NewPaymentMethodSelect.setSelectedOption('all');
    // The pickup opens as the merchant's warehouse (2026-10-01): filled in, not fixed.
    if (!NewPickupAddressInput.text) {
      await BoWarehouse.run();
      const w = (BoWarehouse.data || [])[0];
      if (w && w.address && !NewPickupAddressInput.text) {
        await NewPickupAddressInput.setValue(w.address);
        NewPickupLatHidden.setValue(String(w.lat));
        NewPickupLngHidden.setValue(String(w.lng));
      }
    }
    showModal('CreateOrderModal');
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
    NewPaymentMethodSelect.setSelectedOption('all');
    // The next order starts without the last one's choices (Ico, 2026-10-02): an "Обявена
    // стойност" left on "Да" with its value silently added the service - and its fee - to the
    // following order. The delivery type is emptied too, so it is chosen each time; Създай
    // refuses an order without one ("Изберете вид доставка").
    DeclaredValueSelect.setSelectedOption('no');
    DeclaredValueInput.setValue('');
    OrderShippingSelect.setSelectedOption('');
  }
  }
