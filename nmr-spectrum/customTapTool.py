#!/usr/bin/python

from bokeh.models.callbacks import CustomJS
from bokeh.models.tools import TapTool

class CustomTapTool:

    CALLBACK = """
        /// get BoxSelectTool dimensions from cb_data parameter of Callback
        var geometry = cb_data['geometries'];

        var frame = this.plot_model.frame;

        var xm = frame.xscales['default'];
        var x = xm.invert(geometry.sx);

        var ym = frame.yscales['default'];
        var y = ym.invert(geometry.sy);
        
        button.data = {
            'x': x,
            'y': y
        };

        if (text) {
            text.value = x.toString();
        }
    """

    AUTO = """
        button.clicks++;
    """

    def __init__(self, logger, button, text=None, tapTool=TapTool, auto=False):
        self.logger = logger

        callback = CustomJS(args=dict(text=text, button=button), code=self.CALLBACK + (self.AUTO if auto else ""))
        self.tapTool = tapTool(callback=callback)

    def addToPlot(self, plot):
        plot.add_tools(self.tapTool)
