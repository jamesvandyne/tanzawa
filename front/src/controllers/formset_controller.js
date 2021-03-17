import { Controller } from "stimulus"

export default class extends Controller {
    static get targets() {
        return ["add", "forms", "emptyForm"]
    }


    toggleText(event) {
        if(event.target.checked) {
            event.target.labels[0].innerText = "Undo";
        } else {
            event.target.labels[0].innerText = "Remove";
        }
    }

    addForm(event) {
        const totalFormInput = document.getElementById(event.target.dataset.totalFormId);
        const count = totalFormInput.value;
        const emptyForm = this.emptyFormTarget.innerHTML.replace(/__prefix__/g, count);
        this.formsTarget.insertAdjacentHTML('beforeend', emptyForm);
        totalFormInput.value = parseInt(count) + 1;
    }

}