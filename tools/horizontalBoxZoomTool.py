from bokeh.models import Drag, BoxAnnotation, DEFAULT_BOX_OVERLAY
from bokeh.core.properties import Instance, Enum, Bool
from bokeh.core.enums import Dimensions

class HorizontalBoxZoomTool(Drag):

    __implementation__ = "horizontalBoxZoomTool.ts"

    dimensions = Enum(Dimensions, default="both")
    overlay = Instance(BoxAnnotation, default=DEFAULT_BOX_OVERLAY)
    match_aspect = Bool(default=False)
