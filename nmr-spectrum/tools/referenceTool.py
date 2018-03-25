#################################################
# Title: Bokeh                                  #
# Code version: 12.14                           #
# Availability: https://github.com/bokeh/bokeh  #
#################################################

from bokeh.core.properties import List, String, Instance, Enum
from bokeh.models.tools import Tap
from bokeh.models.renderers import Renderer
from bokeh.models.callbacks import Callback

class ReferenceTool(Tap):

    __implementation__ = "referenceTool.ts"

    names = List(String)

    renderers = List(Instance(Renderer))

    behavior = Enum("select", "inspect", default="inspect")

    callback = Instance(Callback)
