/************************************************
 * Title: Bokeh                                 *
 * Code version: 12.14                          *
 * Availability: https://github.com/bokeh/bokeh *
 ************************************************/

import {SelectTool, SelectToolView} from "models/tools/gestures/select_tool"
import {BoxAnnotation} from "models/annotations/box_annotation"
import * as p from "core/properties"
import {Dimensions} from "core/enums"
import {RectGeometry} from "core/geometry"
import {extend} from "core/util/object"

export interface BkEv {
  bokeh: {
    sx: number
    sy: number
  }
  srcEvent: {
    shiftKey?: boolean
  }
}

export class BothDimensionsSelectToolView extends SelectToolView {
  model: BothDimensionsSelectTool

  protected _base_point: [number, number] | null
  protected _zeroPoint: number

  _pan_start(e: BkEv): void {
    const {sx, sy} = e.bokeh
    this._base_point = [sx, sy]

    const frame = this.plot_model.frame
    const ym = frame.yscales['default']
    this._zeroPoint = ym.compute(0)
  }

  _pan(e: BkEv): void {
    const {sx, sy} = e.bokeh
    const curpoint: [number, number] = [sx, sy]

    const dist = Math.abs(this._zeroPoint - sy)

    const frame = this.plot_model.frame
    const [sxlim, sylim] = this.model._get_dim_limits(this._base_point!, curpoint, frame, "width")

    if(this._zeroPoint - dist > sylim[0]) {
        this.model.overlay.update({left: sxlim[0], right: sxlim[1], top: sylim[0], bottom: this._zeroPoint - dist})
    } else if (this.model.overlay.left !== null) {
        this.model.overlay.update({left: null, right: null, top: null, bottom: null})
    }
    if(this._zeroPoint + dist < sylim[1]) {
      this.model.overlayDown.update({left: sxlim[0], right: sxlim[1], top: this._zeroPoint + dist, bottom: sylim[1]})
    } else if (this.model.overlayDown.left !== null) {
      this.model.overlayDown.update({left: null, right: null, top: null, bottom: null})
    }

    if (this.model.select_every_mousemove) {
      const append = e.srcEvent.shiftKey || false
      this._do_select(sxlim, sylim, false, append, e)
    }
  }

  _pan_end(e: BkEv): void {

    const {sx, sy} = e.bokeh
    const curpoint: [number, number] = [sx, sy]

    const frame = this.plot_model.frame

    const [sxlim, sylim] = this.model._get_dim_limits(this._base_point!, curpoint, frame, "width")
    const append = e.srcEvent.shiftKey || false
    this._do_select(sxlim, sylim, true, append, e)

    this.model.overlay.update({left: null, right: null, top: null, bottom: null})
    this.model.overlayDown.update({left: null, right: null, top: null, bottom: null})

    this._base_point = null

    this.plot_view.push_state('box_select', {selection: this.plot_view.get_selection()})
  }

  _do_select([sx0, sx1]: [number, number], [sy0, sy1]: [number, number], final: boolean, append: boolean = false, e: BkEv): void {

    const {sx, sy} = e.bokeh
    const frame = this.plot_model.frame
    const xm = frame.xscales['default']
    const ym = frame.yscales['default']

    const geometry: RectGeometry = {
      type: 'rect',
      sx0: sx0,
      sx1: sx1,
      sy0: sy0,
      sy1: sy1,
      x: xm.invert(sx),
      y: ym.invert(sy),
    }
    this._select(geometry, final, append)
  }

  _emit_callback(geometry: RectGeometry): void {
    const r = this.computed_renderers[0]
    const frame = this.plot_model.frame

    const xscale = frame.xscales[r.x_range_name]
    const yscale = frame.yscales[r.y_range_name]

    const {sx0, sx1, sy0, sy1} = geometry
    const [x0, x1] = xscale.r_invert(sx0, sx1)
    const [y0, y1] = yscale.r_invert(sy0, sy1)

    const g = extend({x0, y0, x1, y1}, geometry)
    this.model.callback.execute(this.model, {geometry: g})
  }
}

const DEFAULT_BOX_OVERLAY = () => {
  return new BoxAnnotation({
    level: "overlay",
    render_mode: "css",
    top_units: "screen",
    left_units: "screen",
    bottom_units: "screen",
    right_units: "screen",
    fill_color: {value: "#ff3333"},
    fill_alpha: {value: 0.5},
    line_color: {value: "red"},
    line_alpha: {value: 1.0},
    line_width: {value: 2},
    line_dash: {value: [4, 4]},
  })
}

export namespace BothDimensionsSelectTool {
  export interface Attrs extends SelectTool.Attrs {
    tool_name: string
    icon: string

    dimensions: Dimensions
    select_every_mousemove: boolean
    callback: any // XXX
    overlay: BoxAnnotation,
    overlayDown: BoxAnnotation
  }

  export interface Opts extends SelectTool.Opts {}
}

export interface BothDimensionsSelectTool extends BothDimensionsSelectTool.Attrs {}

export class BothDimensionsSelectTool extends SelectTool {

  constructor(attrs?: Partial<BothDimensionsSelectTool.Attrs>, opts?: BothDimensionsSelectTool.Opts) {
    super(attrs, opts)
    this.tool_name = attrs.tool_name
    this.icon = attrs.icon
  }

  static initClass() {
    this.prototype.type = "BothDimensionsSelectTool"

    this.prototype.default_view = BothDimensionsSelectToolView

    this.define({
      tool_name:              [ p.String ],
      icon:                   [ p.String ],
      dimensions:             [ p.Dimensions, "both"            ],
      select_every_mousemove: [ p. Bool,    false               ],
      callback:               [ p.Instance                      ],
      overlay:                [ p.Instance, DEFAULT_BOX_OVERLAY ],
      overlayDown:            [ p.Instance, DEFAULT_BOX_OVERLAY ],
    })
  }

  tool_name = "Box Select"
  icon = "bk-tool-icon-box-select"
  event_type = "pan"
  default_order = 30

  get tooltip(): string {
    return this._get_dim_tooltip(this.tool_name, this.dimensions)
  }
}

BothDimensionsSelectTool.initClass()
