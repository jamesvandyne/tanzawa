import { Controller } from 'stimulus'

export default class extends Controller {

  static get targets() {
      return ['item'];
  }
  static get classes() {
      return ['hidden'];
  }

  connect () {
    this.class = this.hasHiddenClass ? this.hiddenClass : 'hidden'
  }

  toggle () {
    this.itemTargets.forEach(item => {
      item.classList.toggle(this.class)
    })
  }

  show () {
    this.itemTargets.forEach(item => {
      item.classList.remove(this.class)
    })
  }

  hide () {
    this.itemTargets.forEach(item => {
      item.classList.add(this.class)
    })
  }
}