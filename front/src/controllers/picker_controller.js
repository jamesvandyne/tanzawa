import { Controller } from 'stimulus'

export default class extends Controller {

    static get targets() {
        return ['form'];
    }

    initialize() {
        this.trix = document.getElementsByTagName("trix-editor")[0].editor;
        this.url = this.data.get('url');
    }

    insertIntoPost(e) {
        fetch(e.target.dataset.url).then(response => {
            if (response.ok) {
                return response.text()
            }
        })
        .then(html => {
            if(html) {
                this.trix.insertHTML(html);
            }
        })
    }
}