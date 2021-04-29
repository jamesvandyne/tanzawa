import { Controller } from 'stimulus'

export default class extends Controller {

    static get targets() {
        return ['wrapper', 'container', 'content', 'background'];
    }

    initialize() {
        this.url = this.data.get('url');
        this.open = true;
    }

    view(e) {
        if (e.target !== this.wrapperTarget &&
            !this.wrapperTarget.contains(e.target)) {
            return;
        }

        if (this.open) {
            this.getContent(this.url)
            this.wrapperTarget.insertAdjacentHTML('afterbegin', this.template())
        } else {
            console.log("closed");
        }
    }

    close(e) {
        e.preventDefault()

        if (this.open) {
            if (this.hasContainerTarget) {
                this.containerTarget.remove()
            }
        }
    }

    closeBackground(e) {
        if (e.target === this.backgroundTarget) {
            this.close(e)
        }
    }

    closeWithKeyboard(e) {
        if (e.keyCode === 27) {
            this.close(e)
        }
    }

    getContent(url) {
        fetch(url).then(response => {
            if (response.ok) {
                return response.text()
            }
        })
            .then(html => {
                this.contentTarget.innerHTML = html
            })
    }

    template() {
        return `
      <div data-remote-target='container'>
        <div class='modal-wrapper' data-remote-target='background' data-action='click->remote#closeBackground'>
          <div class='fixed left-0 top-0 rounded z-20 w-full h-screen bg-opacity-25 bg-bianca-900 overflow-auto flex justify-center' data-remote-target='content'>
          <span class='loader-spinner m-2'></span>
        </div>

        <button data-action='click->remote#close' class='absolute top-0 right-0 w-6 h-6 m-1 text-white z-20 m-2'>
          <svg width='24' height='24' viewBox='0 0 24 24' fill='none'>
            <path d='M6 18L18 6M6 6L18 18' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' />
          </svg>
        </button>
        </div>
      </div>
    `
    }
}