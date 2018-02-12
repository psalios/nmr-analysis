from bokeh.models import Scroll
from bokeh.core.properties import List, Enum
from bokeh.core.enums import Dimensions

class FixedWheelZoomTool(Scroll):
    __implementation__ = "fixedWheelZoomTool.ts"

    dimensions = Enum(Dimensions, default="both")
