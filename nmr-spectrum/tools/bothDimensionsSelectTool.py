from bokeh.models import Drag, BoxAnnotation, DEFAULT_BOX_OVERLAY
from bokeh.core.properties import Instance, Enum, Bool, List, String
from bokeh.models.renderers import Renderer
from bokeh.models.callbacks import Callback
from bokeh.core.enums import Dimensions

class BothDimensionsSelectTool(Drag):

    __implementation__ = "bothDimensionsSelectTool.ts"

    tool_name = String("Box Select")
    icon = String("bk-tool-icon-box-select")
    names = List(String)

    renderers = List(Instance(Renderer))

    select_every_mousemove = Bool(False)

    dimensions = Enum(Dimensions, default="both")

    callback = Instance(Callback)

    overlay = Instance(BoxAnnotation, default=DEFAULT_BOX_OVERLAY)
    overlayDown = Instance(BoxAnnotation, default=DEFAULT_BOX_OVERLAY)

    def addToPlot(self, plot):
        plot.add_layout(self.overlayDown)
        plot.add_tools(self)
