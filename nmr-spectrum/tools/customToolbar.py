#################################################
# Title: Bokeh                                  #
# Code version: 12.14                           #
# Availability: https://github.com/bokeh/bokeh  #
#################################################

from bokeh.core.properties import Instance
from bokeh.models.tools import Toolbar, Drag, Inspection, Scroll, Tool

class CustomToolbar(Toolbar):

    __implementation__ = "customToolbar.ts"
