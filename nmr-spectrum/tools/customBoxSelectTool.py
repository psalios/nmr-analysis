from bokeh.models import Drag, BoxAnnotation, DEFAULT_BOX_OVERLAY
from bokeh.core.properties import Instance, Enum, Bool, List, String
from bokeh.models.renderers import Renderer
from bokeh.models.callbacks import Callback
from bokeh.core.enums import Dimensions

class CustomBoxSelectTool(Drag):

    __implementation__ = "customBoxSelectTool.ts"

    tool_name = String("Box Select")

    icon = String("bk-tool-icon-box-select")

    names = List(String)

    renderers = List(Instance(Renderer))

    select_every_mousemove = Bool(False)

    dimensions = Enum(Dimensions, default="both")

    callback = Instance(Callback)

    overlay = Instance(BoxAnnotation, default=DEFAULT_BOX_OVERLAY)
