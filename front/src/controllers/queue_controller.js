import { Controller } from "stimulus"

export default class extends Controller {
    processQueue = false;

    static get targets() {
        return ["start", "item", "emptyForm"]
    }

    connect() {
        this.processQueue = true;
        this.importItem();
    }

    importItem() {

    }

}