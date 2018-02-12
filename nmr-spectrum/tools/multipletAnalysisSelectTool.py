from bokeh.models import Drag, BoxAnnotation, DEFAULT_BOX_OVERLAY
from bokeh.core.properties import Instance, Enum, Bool, List, String
from bokeh.models.renderers import Renderer
from bokeh.models.callbacks import Callback
from bokeh.core.enums import Dimensions

class MultipletAnalysisSelectTool(Drag):

    __implementation__ = "multipletAnalysisSelectTool.ts"

    names = List(String)

    renderers = List(Instance(Renderer))

    select_every_mousemove = Bool(False)

    dimensions = Enum(Dimensions, default="both")

    callback = Instance(Callback)

    overlay = Instance(BoxAnnotation, default=DEFAULT_BOX_OVERLAY)
