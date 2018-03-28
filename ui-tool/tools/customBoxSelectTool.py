#################################################
# Title: Bokeh                                  #
# Code version: 12.14                           #
# Availability: https://github.com/bokeh/bokeh  #
#################################################

from bokeh.models import Drag, BoxAnnotation, DEFAULT_BOX_OVERLAY
from bokeh.core.properties import Instance, Enum, Bool, List, String
from bokeh.models.renderers import Renderer
from bokeh.models.callbacks import Callback
from bokeh.core.enums import Dimensions

_DEFAULT_BOX_ANNOTATION = lambda: BoxAnnotation(
    level="overlay",
    render_mode="css",
    top_units="screen",
    left_units="screen",
    bottom_units="screen",
    right_units="screen",
    fill_color="#ff3333",
    fill_alpha=0.5,
    line_color="red",
    line_alpha=1.0,
    line_width=2,
    line_dash=[4, 4]
)

class CustomBoxSelectTool(Drag):

    __implementation__ = "customBoxSelectTool.ts"

    tool_name = String("Box Select")

    icon = String("bk-tool-icon-box-select")

    names = List(String)

    renderers = List(Instance(Renderer))

    select_every_mousemove = Bool(False)

    dimensions = Enum(Dimensions, default="both")

    callback = Instance(Callback)

    overlay = Instance(BoxAnnotation, default=_DEFAULT_BOX_ANNOTATION)

    query = String("")
