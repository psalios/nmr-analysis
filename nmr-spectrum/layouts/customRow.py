from bokeh.core.properties import Bool
from bokeh.models.layouts import Box

class CustomRow(Box):

    __implementation__ = "customRow.ts"

    hide = Bool(False)
