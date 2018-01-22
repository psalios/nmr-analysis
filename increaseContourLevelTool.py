from bokeh.models import Action

INCREASECONTOURLEVELJS = """
p = require "core/properties"
ActionTool = require "models/tools/actions/action_tool"

class IncreaseContourLevelToolView extends ActionTool.View

  do: () ->
    increaseContourLevel()

class IncreaseContourLevelTool extends ActionTool.Model
  default_view: IncreaseContourLevelToolView
  type: "IncreaseContourLevelTool"
  tool_name: "Decrease Contour Level"
  icon: "bk-tool-icon-redo"

module.exports = {
  Model: IncreaseContourLevelTool
  View: IncreaseContourLevelToolView
}
"""

class IncreaseContourLevelTool(Action):
    __implementation__ = INCREASECONTOURLEVELJS
