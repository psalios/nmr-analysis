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

    @staticmethod
    def Create(button, id, text=None, tapTool=TapTool, auto=False):
        callback = CustomJS(args=dict(text=text, button=button), code=CustomTapTool.CALLBACK + (CustomTapTool.AUTO if auto else ""))
        return tapTool(id=id, callback=callback)
