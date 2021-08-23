import { Controller } from "stimulus"
import L from 'leaflet';


export default class extends Controller {
    static get targets() {
        return ["map", "entry"]
    }

    connect() {
        const osm = L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png');
        const bounds = new L.LatLngBounds();
        this.map = L.map(this.mapTarget.id, { zoomSnap: 0.1});
        const map = this.map;
        var hasMarker = false;
        const pointList = [];
        this.entryTargets.forEach(entry => {
            const lat = entry.dataset.lat;
            const lon = entry.dataset.lon;
            if (lat && lon) {
                const marker = L.circleMarker([lat, lon], {
                    radius: 5,
                });
                console.log(entry.dataset.name);
                marker.bindPopup(`<p>${entry.dataset.name}</p>`);
                marker.on({
                    mouseover: function () {
                        this.openPopup()
                    },
                    mouseout: function () {
                        this.closePopup()
                    },
                    click: function () {
                        window.open(entry.dataset.bookmark, "_blank");
                    }
                });
                marker.addTo(map);
                bounds.extend(marker.getLatLng());
                hasMarker = true;
                pointList.push(marker);
            }
        });
        // // setup base layer
        osm.addTo(this.map);
        if (hasMarker) {
            map.fitBounds(bounds);

        }
    }

}