from bokeh.models import Action
from bokeh.core.properties import Float

RESETTOOL = """
p = require "core/properties"
ActionTool = require "models/tools/actions/action_tool"

class NewResetToolView extends ActionTool.View

  do: () ->
    @plot_view.x_range._initial_start = @mget('xstart');
    @plot_view.x_range._initial_end = @mget('xend');
    @plot_view.y_range._initial_start = @mget('ystart');
    @plot_view.y_range._initial_end = @mget('yend');

    @plot_view.clear_state()
    @plot_view.reset_range()
    @plot_view.reset_selection()

class NewResetTool extends ActionTool.Model
  default_view: NewResetToolView
  type: "ResetTool"
  tool_name: "Reset"
  icon: "bk-tool-icon-reset"

  @define {
    reset_size: [ p.Bool, true ]
    xstart:     [ p.Int, 0 ]
    xend:       [ p.Int, 0 ]
    ystart:     [ p.Int, 0 ]
    yend:       [ p.Int, 0 ]
  }

module.exports = {
  Model: NewResetTool
  View: NewResetToolView
}
"""

class NewResetTool(Action):
    __implementation__ = RESETTOOL
    xstart = Float(default=0.0)
    xend = Float(default=0.0)
    ystart = Float(default=0.0)
    yend = Float(default=0.0)
