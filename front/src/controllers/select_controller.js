import { Controller } from "stimulus"

export default class extends Controller {
    static get targets() {
        return ["menuItem"]
    }

    static get classes() {
        return ["selected"]
    }

    click(event) {
        this.menuItemTargets.forEach(menuItem => {
            menuItem.classList.remove(this.selectedClass)
        });
        event.target.closest('li').classList.add(this.selectedClass);
    }

}