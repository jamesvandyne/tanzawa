import { Controller } from "stimulus"
import L from 'leaflet';

export default class extends Controller {
    static get targets() {
        return ["map", "entry"]
    }

    connect() {
        if(this.mapTarget.dataset.showMap === "False") {
            return;
        }

        const osm = L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png',
            {
                minZoom: 0,
                maxZoom: 15
            });
        const bounds = new L.LatLngBounds();
        this.map = L.map(this.mapTarget.id);

        const map = this.map;
        var hasMarker = false;
        const start = new L.LatLng(this.mapTarget.dataset.startLat, this.mapTarget.dataset.startLon);
        const pointList = [start];
        bounds.extend(start);
        this.entryTargets.forEach(entry => {
            const lat = entry.dataset.lat;
            const lon = entry.dataset.lon;
            if (lat && lon) {
                const marker = L.marker([lat, lon]).addTo(map);
                marker.bindPopup(entry.querySelector(".p-name").textContent);
                marker.on({
                    mouseover: function () {
                        this.openPopup()
                    },
                    mouseout: function () {
                        this.closePopup()
                    },
                    click: function () {
                        window.open(entry.querySelector("[rel='bookmark']").href, "_blank");
                    }
                });
                pointList.push(marker.getLatLng());
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
        map.fitBounds(bounds);
        // // setup base layer
        osm.addTo(this.map);
        if (hasMarker) {
            map.fitBounds(bounds);
        }
    }

}