from bokeh.models import Action
from bokeh.core.properties import Enum, Percent
from bokeh.core.enums import Dimensions

class FixedZoomOutTool(Action):

    __implementation__ = "fixedZoomOutTool.ts"

    dimensions = Enum(Dimensions, default="both")

    factor = Percent(default=0.1)
