/* XXX: partial */
import * as p from "core/properties"
import {register_with_event, ButtonClick} from "core/bokeh_events"

import {AbstractButton, AbstractButtonView} from "models/widgets/abstract_button"

export class ManualPeakPickingButtonView extends AbstractButtonView {
  model: ManualPeakPickingButton

  change_input(): void {
    if (Object.keys(this.model.data).length === 0) {
      alert("Please select area using the select tool.")
    } else {
      this.model.trigger_event(new ButtonClick({}))
      this.model.clicks = this.model.clicks + 1
      super.change_input()
    }
  }
}

export class ManualPeakPickingButton extends AbstractButton {

  static initClass() {
    this.prototype.type = "ManualPeakPickingButton"
    this.prototype.default_view = ManualPeakPickingButtonView

    this.define({
      clicks: [ p.Number, 0 ],
      data: [ p.Any, {} ]
    })

    register_with_event(ButtonClick, this)
  }

  clicks: number
  data: any;
}

ManualPeakPickingButton.initClass()
