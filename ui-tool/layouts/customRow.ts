import * as p from "core/properties"
import {Box, BoxView} from "models/layouts/box"

export class CustomRowView extends BoxView {
  model: CustomRow

  css_classes(): string[] {
    let css_classes = super.css_classes().concat("bk-grid-row")
    if(this.model.hide) {
      css_classes = css_classes.concat("custom-class-hide")
    }
    return css_classes
  }
}

export namespace CustomRow {
  export interface Attrs extends Box.Attrs {}

  export interface Opts extends Box.Opts {}
}

export interface CustomRow extends CustomRow.Attrs {}

export class CustomRow extends Box {

  constructor(attrs?: Partial<CustomRow.Attrs>, opts?: CustomRow.Opts) {
    super(attrs, opts)
  }

  static initClass() {
    this.prototype.type = "CustomRow"
    this.prototype.default_view = CustomRowView

    this.define({
        hide: [ p.Bool, false ]
    })
  }

  hide: boolean
  _horizontal = true
}
CustomRow.initClass()
