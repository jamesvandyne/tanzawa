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
                    radius: 20}),
                zoom: 8
            },
            {
                marker: L.circleMarker(latlng, {
                    color: this.color,
                    fillColor: this.fillColor,
                    fillOpacity: 0.5,
                    radius: 30}),
                zoom: 14
            },
        ];

        // setup base layer
        osm.addTo(this.map);
        this.changeZoom(0);

        // setup event handlers
        this.map.on('click', event => this.mapClicked(event));
        this.mapTarget.addEventListener('mouseenter', event => this.mapEntered(event));
        this.mapTarget.addEventListener('mouseleave', event =>  this.mapExited(event));
        this.zoomLevels[1].marker.on('mouseover', event => this.mouseOverMarker(event));
        this.zoomLevels[2].marker.on('mouseout', event => this.leaveCenter(event));
    }

    changeZoom(zoomIndex) {
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
        setTimeout(() => {this.changeZoom(1)}, 200);
    }

    mapExited(event) {
        event.preventDefault();
        this.inMap = false;
        this.nearCenter = false;
        setTimeout(() => {this.changeZoom(0)}, 200);
    }

    mouseOverMarker(event) {
        if(this.nearCenter) {
            return;
        }
        this.nearCenter = true;
        setTimeout(() => {this.changeZoom(2)}, 200);
    }

    leaveCenter(event) {
        this.nearCenter = false;
        setTimeout(() => {this.changeZoom(1)}, 200);
    }

    async mapClicked(e) {
        this.changeZoom(this.zoomIndex + 1);
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