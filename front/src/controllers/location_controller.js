import { Controller } from "stimulus"

export default class extends Controller {
    static get targets() {
        return ["map", "address", "locality", "region", "country", "zip"]
    }

    static get classes() {
        return ["selected"]
    }

    connect() {
        // this.mapTarget
        // var mymap = L.map('leaflet').setView([51.505, -0.09], 13);
        // var osm = L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {minZoom: 0, maxZoom: 9});
        // osm.addTo(mymap);
    }

}