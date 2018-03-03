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

export class MeasureJToolView extends SelectToolView {
  model: MeasureJTool

  protected _base_point: [number, number] | null

  _pan_start(e: BkEv): void {
    const {sx, sy} = e.bokeh
    this._base_point = [sx, sy]

    const frame = this.plot_model.frame
    const ym = frame.yscales['default']

    const [_, sylim] = this.model._get_dim_limits(this._base_point!, this._base_point!, frame, "width")
    const y0 = ym.invert(sylim[0])
    const y1 = ym.invert(sylim[1])
    const ymid = (y0 + y1) / 2
    this.model.label.y = ymid
  }

  _pan(e: BkEv): void {
    const {sx, sy} = e.bokeh
    const curpoint: [number, number] = [sx, sy]

    const frame = this.plot_model.frame
    const xm = frame.xscales['default'];

    const [sxlim, sylim] = this.model._get_dim_limits(this._base_point!, curpoint, frame, "width")

    const x0 = xm.invert(sxlim[0])
    const x1 = xm.invert(sxlim[1])
    const val = (x0 - x1) * this.model.frequency
    const text = val.toFixed(1).toString() + " Hz"

    this.model.label.x = x1
    this.model.label.text = text

    this.model.overlay.update({left: sxlim[0], right: sxlim[1], top: sylim[0], bottom: sylim[1]})

    if (this.model.select_every_mousemove) {
      const append = e.srcEvent.shiftKey || false
      this._do_select(sxlim, sylim, false, append)
    }
  }

  _pan_end(e: BkEv): void {
    const {sx, sy} = e.bokeh
    const curpoint: [number, number] = [sx, sy]

    const frame = this.plot_model.frame

    const [sxlim, sylim] = this.model._get_dim_limits(this._base_point!, curpoint, frame, "width")
    const append = e.srcEvent.shiftKey || false
    this._do_select(sxlim, sylim, true, append)

    this.model.overlay.update({left: null, right: null, top: null, bottom: null})
    this.model.label.text = "";

    this._base_point = null

    this.plot_view.push_state('box_select', {selection: this.plot_view.get_selection()})
  }

  _do_select([sx0, sx1]: [number, number], [sy0, sy1]: [number, number], final: boolean, append: boolean = false): void {
    const geometry: RectGeometry = {
      type: 'rect',
      sx0: sx0,
      sx1: sx1,
      sy0: sy0,
      sy1: sy1,
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
    fill_color: {value: "lightgrey"},
    fill_alpha: {value: 0.5},
    line_color: {value: "black"},
    line_alpha: {value: 1.0},
    line_width: {value: 2},
    line_dash: {value: [4, 4]},
  })
}

export namespace MeasureJTool {
  export interface Attrs extends SelectTool.Attrs {
    dimensions: Dimensions
    select_every_mousemove: boolean
    callback: any // XXX
    overlay: BoxAnnotation
    frequency: number
    label: any
  }

  export interface Opts extends SelectTool.Opts {}
}

export interface MeasureJTool extends MeasureJTool.Attrs {}

export class MeasureJTool extends SelectTool {

  constructor(attrs?: Partial<MeasureJTool.Attrs>, opts?: MeasureJTool.Opts) {
    super(attrs, opts)
  }

  static initClass() {
    this.prototype.type = "MeasureJTool"

    this.prototype.default_view = MeasureJToolView

    this.define({
      dimensions:             [ p.Dimensions, "both"            ],
      select_every_mousemove: [ p.Bool,    false                ],
      callback:               [ p.Instance                      ],
      overlay:                [ p.Instance, DEFAULT_BOX_OVERLAY ],
      frequency:              [ p.Int, 500                      ],
      label:                  [ p.Instance                      ],
    })
  }

  tool_name = "Measure J"
  icon = "my_icon_measure_j"
  event_type = "pan"
  default_order = 30

  get tooltip(): string {
    return this._get_dim_tooltip(this.tool_name, this.dimensions)
  }
}

MeasureJTool.initClass()
