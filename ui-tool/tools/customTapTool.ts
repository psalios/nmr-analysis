/************************************************
 * Title: Bokeh                                 *
 * Code version: 12.14                          *
 * Availability: https://github.com/bokeh/bokeh *
 ************************************************/

 import {SelectTool, SelectToolView} from "models/tools/gestures/select_tool"
 import {TapToolView} from "models/tools/gestures/tap_tool"
 import * as p from "core/properties"
 import {TapEvent} from "core/ui_events"
 import {isFunction} from "core/util/types"
 import {Geometry, PointGeometry} from "core/geometry"
 import {DataSource} from "models/sources/data_source"

 export namespace CustomTapTool {
   export interface Attrs extends SelectTool.Attrs {
     behavior: "select" | "inspect"
     callback: any
   }

   export interface Props extends SelectTool.Props {}
 }

 export interface CustomTapTool extends CustomTapTool.Attrs {}

 export class CustomTapTool extends SelectTool {

   properties: CustomTapTool.Props

   constructor(attrs?: Partial<CustomTapTool.Attrs>) {
     super(attrs)
   }

   static initClass(): void {
     this.prototype.type = "CustomTapTool"
     this.prototype.default_view = TapToolView

     this.define({
       behavior: [ p.String, "select" ],
       callback: [ p.Any ],
     })
   }

   tool_name = "Delete Selection"
   icon = "my_icon_remove_selection"
   event_type = "tap" as "tap"
   default_order = 10
 }

 CustomTapTool.initClass()
