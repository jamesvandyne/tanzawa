import { Controller } from "stimulus"

export default class extends Controller {
    static get targets() {
        return ["map", "serialize"]
    }

    static get classes() {
        return ["selected"]
    }

    connect() {
        const defaultLat = this.mapTarget.dataset.defaultLat;
        const defaultLon = this.mapTarget.dataset.defaultLon;
        const defaultZoom = this.mapTarget.dataset.defaultZoom;
        const osm = L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {minZoom: 0, maxZoom: 12});
        this.map = L.map(this.mapTarget.id).setView([defaultLat, defaultLon], defaultZoom);
        this.initial_value = this.serializeTarget.value;
        osm.addTo(this.map);

        if(this.initial_value) {
            const feature = JSON.parse(this.initial_value);
            this.marker = L.marker(feature.coordinates);
            // Center/zoom the map
            this.map.setView(feature.coordinates, this.defaultZoom);
        } else {
            this.marker = L.marker([defaultLat , defaultLon]);
        }
        this.marker.addTo(this.map);

        this.map.on('click', event => this.moveMarker(event));
    }

    moveMarker(e) {
        this.marker.remove();
        this.marker = L.marker(e.latlng);
        this.marker.addTo(this.map);
        this.map.setView(Object.values(e.latlng));
        this.serializePoint(e.latlng);
    }

    serializePoint(latlng) {
        this.serializeTarget.value = JSON.stringify({
            type: "Point",
            coordinates: [latlng.lat, latlng.lng]
        });
    }

}