import { Controller } from "stimulus"
import L from 'leaflet';

export default class extends Controller {
    static get targets() {
        return ["map", "entry"]
    }

    connect() {
        const osm = L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png',
            {

            });
        const bounds = new L.LatLngBounds();
        this.map = L.map(this.mapTarget.id,
            {
                zoomControl: false,
                boxZoom: false,
                doubleClickZoom: false,
                dragging: false,
            }
            );
        const map = this.map;
        var hasMarker = false;
        const pointList = [];
        this.entryTargets.forEach(entry => {
            const lat = entry.dataset.lat;
            const lon = entry.dataset.lon;
            if (lat && lon) {
                const marker = L.circleMarker([lat, lon], {
                    radius: 5,
                }).addTo(map);
                bounds.extend(marker.getLatLng());
                hasMarker = true;
            }
        });

        const firstpolyline = new L.Polyline(pointList, {
            color: 'red',
            weight: 3,
            opacity: 0.5,
            smoothFactor: 1,
            lineCap: 'round'
        });
        firstpolyline.addTo(this.map);
        if(pointList.length) {
            map.fitBounds(bounds);
        }
        // // setup base layer
        osm.addTo(this.map);
        if (hasMarker) {
            map.fitBounds(bounds);
        }
    }

}