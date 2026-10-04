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
    const words = { "бул": "булевард", "б-р": "булевард", "ул": "улица", "пл": "площад",
      "bul": "bulevard", "blvd": "bulevard", "ul": "ulitsa", "pl": "ploshtad" };
    // Latin too (2026-10-04): "bul.slivnica 566" is how merchants type; Google needs the word.
    const expanded = (text || "").replace(/(?<!\p{L})(бул|б-р|ул|пл|bul|blvd|ul|pl)(?:\.|(?=\s))/giu, (m, w) => words[w.toLowerCase()] + " ");
    return expanded.replace(/[ \t]{2,}/g, " ").trim();
  },

  // Latin-typed text in Cyrillic, the way Bulgarians type it on a Latin keyboard: Google's
  // geocoder knows "булевард Сливница" and "Boulevard Slivnitsa" but not "bul.slivnica", so
  // a Latin address is asked once more in Cyrillic (2026-10-04). Text that already has a
  // Cyrillic letter comes back untouched.
  cyrillic: (text) => {
    const t = text || "";
    if (/[\u0400-\u04FF]/.test(t)) return t;
    const map = { sht: "щ", sch: "щ", dzh: "дж", zh: "ж", ch: "ч", sh: "ш", ts: "ц", yu: "ю", ya: "я", ju: "ю", ja: "я", ia: "ия",
      a: "а", b: "б", c: "ц", d: "д", e: "е", f: "ф", g: "г", h: "х", i: "и", j: "й", k: "к", l: "л", m: "м", n: "н", o: "о",
      p: "п", q: "к", r: "р", s: "с", t: "т", u: "у", v: "в", w: "в", x: "кс", y: "й", z: "з" };
    return t.replace(/sht|sch|dzh|zh|ch|sh|ts|yu|ya|ju|ja|ia(?![a-z])|[a-z]/gi, (m) => {
      const out = map[m.toLowerCase()];
      return m[0] === m[0].toUpperCase() && m[0] !== m[0].toLowerCase() ? out[0].toUpperCase() + out.slice(1) : out;
    });
  },

  // The delivery-address search behind Търси and Enter (2026-10-04). Google is asked up to
  // four times, stopping at the first precise answer:
  //   1. the text as typed (abbreviations spelt out) with the postcode as Google's hard
  //      filter - the answer is inside that postcode or there is none;
  //   2. the same in Cyrillic, when the merchant typed Latin ("bul.slivnica" found nothing,
  //      "булевард сливница" finds the building);
  //   3. the postcode as plain text only, which merely nudges - for a postcode Google
  //      disagrees with (a block in ж.к. Младост 1 is 1750 to Google, 1784 to everyone else);
  //   4. if the answer is a town the text never names, once more in Latin (TODO 45).
  // The server runs the same ladder when the order is created.
  searchNewDropoff: async () => {
    const address = (NewDropoffAddressInput.text || "").trim();
    if (address.length < 4) {
      showAlert("Въведете адрес преди да търсите", "warning");
      return false;
    }
    const zip = (NewDropoffPostcodeInput.text || "").trim();
    if (!/^\d{4}$/.test(zip)) {
      showAlert("Въведете пощенския код на получателя (4 цифри) преди да търсите", "warning");
      return false;
    }
    const coarse = ["country", "administrative_area_level_1", "administrative_area_level_2",
      "administrative_area_level_3", "colloquial_area", "political", "locality", "postal_code", "postal_town"];
    const first = () => GeocodeNewDropoffAddress.data?.results?.[0];
    const precise = () => { const r = first(); return !!r && !((r.types || []).length > 0 && r.types.every((t) => coarse.includes(t))); };
    const withZip = (q) => q.includes(zip) ? q : q + ", " + zip + " София";
    const strict = "country:BG|postal_code:" + zip, loose = "country:BG";
    const expanded = LocationManager.expandAbbreviations(address);
    const cyr = LocationManager.cyrillic(expanded);
    try {
      await GeocodeNewDropoffAddress.run({ address: withZip(expanded), components: strict });
      if (!precise() && cyr !== expanded) await GeocodeNewDropoffAddress.run({ address: withZip(cyr), components: strict });
      if (!precise()) await GeocodeNewDropoffAddress.run({ address: withZip(expanded), components: loose });
      if (!first()) {
        showAlert("Адресът не е намерен — проверете изписването", "warning");
        return false;
      }
      let town = LocationManager.wrongTown(first(), address);
      if (town) {
        await GeocodeNewDropoffAddress.run({ address: LocationManager.latinQuery(address) + ", " + zip + " Sofia", components: loose });
        if (first()) town = LocationManager.wrongTown(first(), address);
      }
      if (town) {
        NewDropoffLatHidden.setValue("");
        NewDropoffLngHidden.setValue("");
        showAlert(`Google намира адреса в ${town}, а не в София. Проверете улицата и номера, или изпишете квартала/селото.`, "warning");
        return false;
      }
      LocationManager.updateNewDropoffFromGeocode();
      return true;
    } catch (e) {
      showAlert("Търсенето на адреса не мина. Опитайте пак.", "error");
      return false;
    }
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
