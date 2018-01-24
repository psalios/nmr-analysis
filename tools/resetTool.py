from bokeh.models import Action
from bokeh.core.properties import Float


class NewResetTool(Action):

    __implementation__ = "resetTool.ts"

    xstart = Float(default=0.0)
    xend = Float(default=0.0)
    ystart = Float(default=0.0)
    yend = Float(default=0.0)
