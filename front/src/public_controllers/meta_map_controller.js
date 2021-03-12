import { Controller } from "stimulus"
import L from 'leaflet';

export default class extends Controller {
    static get targets() {
        return ["map", "summary"]
    }

    connect() {
        const defaultLat = this.mapTarget.dataset.defaultLat;
        const defaultLon = this.mapTarget.dataset.defaultLon;
        const defaultZoom = this.mapTarget.dataset.defaultZoom;
        const latlng = [defaultLat, defaultLon];
        const osm = L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png',
            {
                     minZoom: 0,
                     maxZoom: 20});
        this.map = L.map(
            this.mapTarget.id,
            {
                zoomControl: false,
                dragging: false,
                doubleClickZoom: false,
                zoomAnimation: false,
                boxZoom: false,
                fadeAnimation: true
            }
            ).setView(latlng, defaultZoom);
        this.marker = null;
        this.address = {
            'locality': this.mapTarget.dataset.locality,
            'region': this.mapTarget.dataset.region,
            'country': this.mapTarget.dataset.country,
        };
        this.updateSummaryText();
        // setup base layer
        osm.addTo(this.map);

        this.marker = null;
        this.zoomIndex = null;
        this.nearCenter = false;
        this.inMap = false;
        this.zoomLevels = [
            {
                marker: L.circleMarker(latlng, {
                    color: this.color,
                    fillColor: this.fillColor,
                    fillOpacity: 0.5,
                    radius: 10}),
                zoom: 4
            },
            {
                marker: L.circleMarker(latlng, {
                    color: this.color,
                    fillColor: this.fillColor,
                    fillOpacity: 0.5,
                    radius: 15}),
                zoom: 8
            },
            {
                marker: L.circleMarker(latlng, {
                    color: this.color,
                    fillColor: this.fillColor,
                    fillOpacity: 0.5,
                    radius: 20}),
                zoom: 14
            },
        ];
        this.changeZoom(0);
        // setup event handlers
        this.map.on('click', event => this.mapClicked(event));
        this.mapTarget.addEventListener('mouseenter', event => this.mapEntered(event));
        this.mapTarget.addEventListener('mouseleave', event =>  this.mapExited(event));
        this.zoomLevels[1].marker.on('mouseover', event => this.mouseOverMarker(event));
        this.zoomLevels[2].marker.on('mouseout', event => this.leaveCenter(event));
    }

    changeZoom(zoomIndex) {
        console.log("changing zoom " + zoomIndex);
        if(zoomIndex === 2) {
            // debugger;
        }
        if(zoomIndex === this.zoomIndex) {
            return;
        }
        if(this.marker) {
            this.marker.removeFrom(this.map);
        }
        this.zoomIndex = zoomIndex;
        let circle = this.zoomLevels[zoomIndex];
        if(!circle) {
            this.zoomIndex = 0;
            circle = this.zoomLevels[0];
        }
        this.marker = circle.marker;

        this.marker.addTo(this.map);
        this.map.setZoom(circle.zoom);
    }

    mapEntered(event) {
        if(this.inMap) {
            return;
        }
        this.inMap = true;
        console.log("Map entered");
        this.changeZoom(1);
    }

    mapExited(event) {
        event.preventDefault();
        console.log("Leaving");
        this.inMap = false;
        this.nearCenter = false;
        this.changeZoom(0);
    }

    mouseOverMarker(event) {
        // event.stopPropagation();
        if(this.nearCenter) {
            return;
        }
        this.nearCenter = true;
        console.log(`OVER: ${this.zoomIndex}`);
        this.changeZoom(2);
    }

    leaveCenter(event) {
        this.nearCenter = false;
        this.changeZoom(1);
    }


    async mapClicked(e) {
        this.changeZoom(this.zoomIndex + 1);
    }

     updateSummaryText() {
        this.summaryTarget.innerText = [this.address.locality,
                                   this.address.region,
                                   this.address.country].filter(val => val).join(", ");
    }


    serializePoint(latlng) {
        this.serializeTarget.value = JSON.stringify({
            type: "Point",
            coordinates: [latlng.lat, latlng.lng]
        });
    }

    get color() {
        // bianca-500
        return "#fbf7ef";
    }

    get fillColor() {
        // bianca-900
        return "#7b7975";
    }

}