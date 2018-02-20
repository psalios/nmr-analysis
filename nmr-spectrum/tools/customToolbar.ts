import * as p from "core/properties"
import {empty, div} from "core/dom";
import {DOMView} from "core/dom_view";
import {build_views, remove_views} from "core/build_views";
import {logger} from "core/logging"

import {Tool} from "models/tools/tool"
import {ActionTool} from "models/tools/actions/action_tool";
import {HelpTool} from "models/tools/actions/help_tool";
import {GestureTool} from "models/tools/gestures/gesture_tool";
import {InspectTool} from "models/tools/inspectors/inspect_tool";

import {Toolbar} from "models/tools/toolbar"
import {ButtonToolButtonView} from "models/tools/button_tool"

export class CustomToolbarView extends DOMView {
  model: CustomToolbar

  initialize(options: any): void {
    super.initialize(options);
    this._tool_button_views = {};
    this._build_tool_button_views();
  }

  connect_signals(): void {
    super.connect_signals();
    this.connect(this.model.properties.tools.change, () => this._build_tool_button_views());
  }

  remove() {
    remove_views(this._tool_button_views);
    return super.remove();
  }

  _build_tool_button_views(): ButtonToolButtonView[] {
    const tools = this.model._proxied_tools != null ? this.model._proxied_tools : this.model.tools; // XXX
    return build_views(this._tool_button_views, tools, {parent: this}, tool => tool.button_view);
  }

  render() {
    empty(this.el);

    this.el.classList.add("bk-toolbar");
    this.el.classList.add(`bk-toolbar-${this.model.toolbar_location}`);

    const buttons = [];

    const { gestures } = this.model;
    for (const et in gestures) {
      for (const tool of gestures[et].tools) {
        buttons.push(this._tool_button_views[tool.id].el);
      }
    }

    for (const tool of this.model.actions) {
      buttons.push(this._tool_button_views[tool.id].el);
    }

    for (const tool of this.model.inspectors) {
      if (tool.toggleable) {
        buttons.push(this._tool_button_views[tool.id].el);
      }
    }

    for (const tool of this.model.help) {
      buttons.push(this._tool_button_views[tool.id].el);
    }

    if(buttons.length !== 0) {
        const ordered = []
        ordered.push(buttons[0])
        ordered.push(buttons[6])
        ordered.push(buttons[2])
        ordered.push(buttons[7])
        ordered.push(buttons[3])
        ordered.push(buttons[4])
        ordered.push(buttons[1])
        ordered.push(buttons[5])
        ordered.push(buttons[10])
        ordered.push(buttons[9])
        ordered.push(buttons[11])
        ordered.push(buttons[8])

        const el = div({class: 'bk-button-bar'}, ordered)
        this.el.appendChild(el);
    }

    return this;
  }
}

export namespace CustomToolbar {
    export interface Attrs extends Toolbar.Attrs {}

    export interface Opts extends Toolbar.Opts {}
}

export class CustomToolbar extends Toolbar {

    constructor(attrs?: Partial<CustomToolbar.Attrs>, opts?: CustomToolbar.Opts) {
        super(attrs, opts)
    }

    static initClass() {
        this.prototype.type = "CustomToolbar";
        this.prototype.default_view = CustomToolbarView
    }

    initialize(): void {
        super.initialize();
        this._init_tools();
    }

    connect_signals(): void {
        super.connect_signals()
        this.connect(this.properties.tools.change, () => this._init_tools())
    }

    _init_tools() {
        super._init_tools()

        for(const tool of this.tools) {
            // Bind with callback
            this.connect(tool.properties.active.change, this._activeChange.bind(this, tool));
        }
    }

    _activeChange = tool => {
        if (tool.active) {
            // Deactivate all other Gesture Tools (except scroll)
            if (tool instanceof GestureTool && this.gestures.scroll.tools.indexOf(tool) === -1) {
                for(const t of this.tools) {
                    if((t !== tool) && t.active && (t instanceof GestureTool)) {
                        if(this.gestures.scroll.tools.indexOf(t) === -1) {
                            t.active = false;
                        }
                    }
                }
            }
        }
    }

}
CustomToolbar.initClass();
