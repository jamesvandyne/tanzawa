import { Controller } from "stimulus"
import L from 'leaflet';
import { GeoSearchControl, OpenStreetMapProvider } from 'leaflet-geosearch';


export default class extends Controller {
    static get targets() {
        return ["map",
                "serialize",
                "streetAddress",
                "locality",
                "region",
                "country",
                "postalCode",
                "reset",
                "remove",
                "summary",
                "currentLocation",
        ];
    }

    connect() {
        const defaultLat = this.mapTarget.dataset.defaultLat;
        const defaultLon = this.mapTarget.dataset.defaultLon;
        const defaultZoom = this.mapTarget.dataset.defaultZoom;
        const osm = L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {minZoom: 0, maxZoom: 18});
        this.provider = new OpenStreetMapProvider({
            params: {
                addressdetails: 1
            }
        });
        this.map = L.map(this.mapTarget.id).setView([defaultLat, defaultLon], defaultZoom);
        this.marker = null;
        this.initial_values = {
            'point': this.serializeTarget.value,
            'streetAddress': this.streetAddressTarget.value,
            'locality': this.localityTarget.value,
            'region': this.regionTarget.value,
            'country': this.countryTarget.value,
            'postalCode': this.postalCodeTarget.value
        };
        this.updateSummaryText();
        // setup base layer
        osm.addTo(this.map);

        // set initial point
        this.addMarkerFromJson(this.initial_values.point);

        // add search
        const searchControl = new GeoSearchControl({
            style: 'bar',
            provider: this.provider,
            showMarker: false,
        });
        this.map.addControl(searchControl);
        // setup event handlers
        this.map.on('click', event => this.mapClicked(event));
        this.map.on('geosearch/showlocation', event => this.searchResultSelected(event));
    }

    async mapClicked(e) {
        /* Update marker position and lookup address for the new location */

        this._addMarker(e.latlng);
        this.serializePoint(e.latlng);
        this.resetTarget.classList.remove(["hidden"]);
        this.map.setView(Object.values(e.latlng));
        // lookup closest address to point
        try {
            const mapLocation = await this.reverse(e.latlng);
            if(mapLocation.length) {
                this.updateAddressForm(mapLocation[0].raw.address);
            } else {
                this.updateAddressForm({});
            }
        } catch (e) {
            this.updateAddressForm({});
        }
    }

    searchResultSelected(event) {
        this.resetTarget.classList.remove(["hidden"]);
        this._addMarker(event.marker.getLatLng());
        this.serializePoint(event.marker.getLatLng());
        this.updateAddressForm(event.location.raw.address);
    }

    updateSummaryText() {
        this.summaryTarget.innerText = [this.localityTarget.value,
                                   this.regionTarget.value,
                                   this.countryTarget.value].filter(val => val).join(", ");
    }


    async reverse(latlng)  {
        const url = this.provider.endpoint({
          query: {lat: latlng.lat, lon: latlng.lng},
          type: 1,
        });

        const request = await fetch(url);
        const json = await request.json();
        return this.provider.parse({ data: json });
  }

    serializePoint(latlng) {
        this.serializeTarget.value = JSON.stringify({
            type: "Point",
            coordinates: [latlng.lng, latlng.lat]
        });
    }

    _addMarker(latlng) {
        if(this.marker === null) {
            this.marker = L.marker(latlng);
        } else {
            this.marker.setLatLng(latlng);
        }
        this.marker.addTo(this.map);
        this.removeTarget.classList.remove(["hidden"]);
        return this.marker;
    }

    _removeMarker() {
        if(this.marker !== null) {
            this.marker.removeFrom(this.map);
            this.marker = null;
        }
    }

    addMarkerFromJson(point) {
        if(point) {
            const feature = JSON.parse(point);
            this.marker = this._addMarker(feature.coordinates.reverse());
            // Center/zoom the map
            this.map.setView(feature.coordinates, this.defaultZoom);
        }
    }

    updateAddressForm(addressdetail) {
        const house_number = this.getFirstValueWithKey(addressdetail, ["house_number", "house_name"]);
        this.streetAddressTarget.value = `${house_number} ${this.getFirstValueWithKey(addressdetail, ["road"])}`;
        this.localityTarget.value = this.getFirstValueWithKey(addressdetail, ["municipality", "city", "town", "village"]);
        this.regionTarget.value = this.getFirstValueWithKey(addressdetail, ["region", "state", "province", "state_district", "county"]);
        this.countryTarget.value = this.getFirstValueWithKey(addressdetail, ["country", "country_code"]);
        this.postalCodeTarget.value = this.getFirstValueWithKey(addressdetail, ["postcode"]);
        this.updateSummaryText();
    }


    reset(event) {
        /* reset map form to initial value */
        event.preventDefault();
        this.streetAddressTarget.value = this.initial_values.streetAddress;
        this.localityTarget.value = this.initial_values.locality;
        this.regionTarget.value = this.initial_values.region;
        this.countryTarget.value = this.initial_values.country;
        this.postalCodeTarget.value = this.initial_values.postalCode;
        this._removeMarker();
        this.addMarkerFromJson(this.initial_values.point);
        this.updateSummaryText();
        this.resetTarget.classList.add(["hidden"]);
        this.currentLocationTarget.classList.remove(["hidden"]);
        if(this.initial_values.point) {
            this.removeTarget.classList.remove(["hidden"]);
        } else {
            this.removeTarget.classList.add(["hidden"]);
        }

    }


    getFirstValueWithKey(addressdetail, keys) {
        for ( const key of keys) {
            if(addressdetail[key]) {
                return addressdetail[key];
            }
        }
        return "";
    }

    removeLocation(event) {
        this.streetAddressTarget.value = "";
        this.localityTarget.value = "";
        this.regionTarget.value = "";
        this.countryTarget.value = "";
        this.postalCodeTarget.value = "";
        this.serializeTarget.value = "";
        this._removeMarker();
        event.preventDefault();

        this.removeTarget.classList.add(["hidden"]);
        this.currentLocationTarget.classList.remove(["hidden"]);
        if(this.initial_values.point) {
            this.resetTarget.classList.remove(["hidden"]);
        } else {
            this.resetTarget.classList.add(["hidden"]);
        }
    }

    async getMyLocation(event) {
        event.preventDefault();
        navigator.geolocation.getCurrentPosition(pos => this.getLocationSuccess(pos), (err) => {
            console.log("Error!");
        });
    }

    async getLocationSuccess(position) {
        const coords = position.coords;
        const latlng = [coords.latitude, coords.longitude];
        const latlngDict = {lat: latlng[0], lng: latlng[1]};
        this._addMarker(latlng);
        this.serializePoint(latlngDict);
        this.resetTarget.classList.remove(["hidden"]);
        this.currentLocationTarget.classList.add(["hidden"]);
        this.map.setView(Object.values(latlng));
        // lookup closest address to point
        try {
            const mapLocation = await this.reverse(latlngDict);
            if(mapLocation.length) {
                this.updateAddressForm(mapLocation[0].raw.address);
            } else {
                this.updateAddressForm({});
            }
        } catch (e) {
            this.updateAddressForm({});
        }
    }


}