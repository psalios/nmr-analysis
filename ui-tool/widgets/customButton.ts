/************************************************
 * Title: Bokeh                                 *
 * Code version: 12.14                          *
 * Availability: https://github.com/bokeh/bokeh *
 ************************************************/

import * as p from "core/properties"
import {register_with_event, ButtonClick} from "core/bokeh_events"

import {AbstractButton, AbstractButtonView} from "models/widgets/abstract_button"

export class CustomButtonView extends AbstractButtonView {
  model: CustomButton

  change_input(): void {
    if (Object.keys(this.model.data).length === 0) {
      alert(this.model.error)
    } else {
      this.model.trigger_event(new ButtonClick({}))
      this.model.clicks = this.model.clicks + 1
      super.change_input()
      this.model.data = {}
    }
  }
}

export class CustomButton extends AbstractButton {

  static initClass() {
    this.prototype.type = "CustomButton"
    this.prototype.default_view = CustomButtonView

    this.define({
      clicks: [ p.Number, 0 ],
      data: [ p.Any, {} ],
      error: [ p.String, "" ]
    })

    register_with_event(ButtonClick, this)
  }

  clicks: number
  data: any
  error: string
}

CustomButton.initClass()
