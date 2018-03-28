#################################################
# Title: Bokeh                                  #
# Code version: 12.14                           #
# Availability: https://github.com/bokeh/bokeh  #
#################################################

from bokeh.core.properties import Instance, Enum, Bool, List, String
from bokeh.models.renderers import Renderer
from bokeh.models.callbacks import Callback
from bokeh.models.tools import Tap

class CustomTapTool(Tap):

    __implementation__ = "customTapTool.ts"

    names = List(String)

    renderers = List(Instance(Renderer))

    behavior = Enum("select", "inspect", default="select")

    callback = Instance(Callback)
