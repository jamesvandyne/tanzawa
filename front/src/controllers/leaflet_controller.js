import { Controller } from "stimulus"

export default class extends Controller {
    static get targets() {
        return ["map"]
    }

    static get classes() {
        return ["selected"]
    }

    connect() {
        const defaultLat = this.mapTarget.dataset.defaultLat;
        const defaultLon = this.mapTarget.dataset.defaultLon;
        const defaultZoom = this.mapTarget.dataset.defaultZoom;
        const osm = L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {minZoom: 0, maxZoom: 9});

        this.map = L.map(this.mapTarget.id).setView([defaultLat, defaultLon], defaultZoom);

        osm.addTo(this.map);
        this.marker = L.marker([defaultLat , defaultLon]);
        this.marker.addTo(this.map);

        this.map.on('click', event => this.moveMarker(event));
    }


    moveMarker(e) {
        this.marker.remove();
         this.marker = L.marker(e.latlng);
         this.marker.addTo(this.map);
    }

}