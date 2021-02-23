import { Controller } from "stimulus"

export default class extends Controller {
    static get targets() {
        return ["detail"]
    }

    connect() {
        this.detailTarget.addEventListener("mouseover", this.show);
        this.detailTarget.addEventListener("mouseleave", this.hide);
    }

    show(event) {
        this.toggleAttribute("open", true);
    }

    hide(event) {
        this.removeAttribute("open");
    }

}