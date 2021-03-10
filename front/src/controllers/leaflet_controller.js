import { Controller } from "stimulus"
import L from 'leaflet';
import { GeoSearchControl, OpenStreetMapProvider } from 'leaflet-geosearch';


export default class extends Controller {
    static get targets() {
        return ["map", "serialize", "streetAddress", "locality", "region", "country", "postalCode", "reset"]
    }

    static get classes() {
        return ["selected"]
    }

    connect() {
        const defaultLat = this.mapTarget.dataset.defaultLat;
        const defaultLon = this.mapTarget.dataset.defaultLon;
        const defaultZoom = this.mapTarget.dataset.defaultZoom;
        const osm = L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {minZoom: 0, maxZoom: 12});
        this.provider = new OpenStreetMapProvider({
            params: {
                addressdetails: 1
            }
        });
        this.map = L.map(this.mapTarget.id).setView([defaultLat, defaultLon], defaultZoom);
        this.initial_value = this.serializeTarget.value;

        // setup base layer
        osm.addTo(this.map);

        // set initial point
        if(this.initial_value) {
            const feature = JSON.parse(this.initial_value);
            this.marker = L.marker(feature.coordinates);
            // Center/zoom the map
            this.map.setView(feature.coordinates, this.defaultZoom);
        } else {
            this.marker = L.marker([defaultLat , defaultLon]);
        }
        this.marker.addTo(this.map);

        // add search
        const searchControl = new GeoSearchControl({
            style: 'bar',
            provider: this.provider,
            showMarker: false,
        });
        this.map.addControl(searchControl);
        // setup event handlers
        this.map.on('click', event => this.moveMarker(event));
        this.map.on('geosearch/showlocation', event => this.searchResultSelected(event));
    }

    async moveMarker(e) {
        this.marker.setLatLng(e.latlng);
        this.map.setView(Object.values(e.latlng));
        this.marker.addTo(this.map);

        this.serializePoint(e.latlng);
        // lookup address from point
        try {
            const mapLocation = await this.reverse(e.latlng);
            if(mapLocation.length) {
                this.updateAddressForm(mapLocation[0].raw.address);
            } else {
                this.resetAddressForm();
            }
        } catch (e) {
            this.resetAddressForm();
        }
    }

    searchResultSelected(event) {
        console.log(event);
        this.marker.setLatLng(event.marker.getLatLng());
        this.serializePoint(event.marker.getLatLng());
        this.updateAddressForm(event.location.raw.address);
        this.marker.addTo(this.map);
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
            coordinates: [latlng.lat, latlng.lng]
        });
    }

    updateAddressForm(addressdetail) {
        const house_number = this.getFirstValueWithKey(addressdetail, ["house_number", "house_name"]);
        this.streetAddressTarget.value = `${house_number} ${this.getFirstValueWithKey(addressdetail, ["road"])}`;
        this.localityTarget.value = this.getFirstValueWithKey(addressdetail, ["municipality", "city", "town", "village"]);
        this.regionTarget.value = this.getFirstValueWithKey(addressdetail, ["region", "state", "state_district", "county"]);
        this.countryTarget.value = this.getFirstValueWithKey(addressdetail, ["country", "country_code"]);
        this.postalCodeTarget.value = this.getFirstValueWithKey(addressdetail, ["postcode"]);
    }

    resetAddressForm() {
        this.streetAddressTarget.value = "";
        this.localityTarget.value = "";
        this.regionTarget.value = "";
        this.countryTarget.value = "";
        this.postalCodeTarget.value = "";
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
        this.resetAddressForm();
        this.serializeTarget.value = "";
        this.marker.removeFrom(this.map);
        event.preventDefault();
    }

}