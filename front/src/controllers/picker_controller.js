import { Controller } from 'stimulus'

export default class extends Controller {

    static get targets() {
        return ['form'];
    }

    initialize() {
        this.trix = document.getElementsByTagName("trix-editor")[0].editor;
        this.url = this.data.get('url');
    }

    simulateEscKeyPress() {
        const ev = document.createEvent('KeyboardEvent');
        // 27 is the keycode for esc
        ev.initKeyEvent('keydown', true, true, window, false, false, false, false, 27, 0);
        document.body.dispatchEvent(ev);
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
                this.simulateEscKeyPress();
            }
        })
    }
}