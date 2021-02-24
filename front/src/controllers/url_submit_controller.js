import { Controller } from "stimulus"

export default class extends Controller {
    static get targets() {
        return ["field"]
    }

    connect() {
        this.fieldTarget.addEventListener("blur", this.fetchMeta);
    }

    fetchMeta(event) {
        console.log("BLUR");
    }

}