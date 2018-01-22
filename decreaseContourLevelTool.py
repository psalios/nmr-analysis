from bokeh.models import Action

DECREASECONTOURLEVELJS = """
p = require "core/properties"
ActionTool = require "models/tools/actions/action_tool"

class DecreaseContourLevelToolView extends ActionTool.View

  do: () ->
    decreaseContourLevel()

class DecreaseContourLevelTool extends ActionTool.Model
  default_view: DecreaseContourLevelToolView
  type: "DecreaseContourLevelTool"
  tool_name: "Increase Contour Level"
  icon: "bk-tool-icon-undo"

module.exports = {
  Model: DecreaseContourLevelTool
  View: DecreaseContourLevelToolView
}
"""

class DecreaseContourLevelTool(Action):
    __implementation__ = DECREASECONTOURLEVELJS
