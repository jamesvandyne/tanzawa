import { Controller } from "stimulus"

export default class extends Controller {
    static get targets() {
        return ["field", "form"]
    }
    connect() {
        this.timer = 0;
    }

    input() {
        if(this.timer) {
            clearTimeout(this.timer);
        }
        if(this.fieldTarget.validity.valid) {
            this.timer = setTimeout(() => {
                this.formTarget.requestSubmit();
            }, 400);
        }

    }

}