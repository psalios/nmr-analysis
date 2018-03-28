/************************************************
 * Title: Bokeh                                 *
 * Code version: 12.14                          *
 * Availability: https://github.com/bokeh/bokeh *
 ************************************************/

import {ActionTool, ActionToolView} from "models/tools/actions/action_tool"
import {Dimensions} from "core/enums"
import {scale_range} from "core/util/zoom"

import * as p from "core/properties"

export class FixedZoomOutToolView extends ActionToolView {
  model: FixedZoomOutTool

  doit(): void {
    const frame = this.plot_model.frame
    const dims = this.model.dimensions

    // restrict to axis configured in tool's dimensions property
    const h_axis = dims == 'width'  || dims == 'both'
    const v_axis = false // dims == 'height' || dims == 'both'

    // zooming out requires a negative factor to scale_range
    const zoom_info = scale_range(frame, -this.model.factor, h_axis, v_axis)

    this.plot_view.push_state('zoom_out', {range: zoom_info})
    this.plot_view.update_range(zoom_info, false, true)

    if (this.model.document)
      this.model.document.interactive_start(this.plot_model.plot)
  }
}

export namespace FixedZoomOutTool {
  export interface Attrs extends ActionTool.Attrs {
    factor: number
    dimensions: Dimensions
  }

  export interface Opts extends ActionTool.Opts {}
}

export interface FixedZoomOutTool extends FixedZoomOutTool.Attrs {}

export class FixedZoomOutTool extends ActionTool {

  constructor(attrs?: Partial<FixedZoomOutTool.Attrs>, opts?: FixedZoomOutTool.Opts) {
    super(attrs, opts)
  }

  static initClass() {
    this.prototype.type = "FixedZoomOutTool"
    this.prototype.default_view = FixedZoomOutToolView

    this.define({
      factor:     [ p.Percent,    0.1    ],
      dimensions: [ p.Dimensions, "both" ],
    })
  }

  tool_name = "Zoom Out"
  icon = "bk-tool-icon-zoom-out"

  get tooltip(): string {
    return this._get_dim_tooltip(this.tool_name, this.dimensions)
  }
}

FixedZoomOutTool.initClass()
