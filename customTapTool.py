from bokeh.models.callbacks import CustomJS
from bokeh.models.tools import TapTool

class CustomTapTool:

    CALLBACK = """
        /// get BoxSelectTool dimensions from cb_data parameter of Callback
        var geometry = cb_data['geometries'];

        var frame = this.plot_model.frame;
        var xm = frame.xscales['default'];

        var x = xm.invert(geometry.sx);
        button.data = {
            'x': x
        };
        text.value = x.toString();
    """

    def __init__(self, logger, text, button, tapTool=TapTool):
        self.logger = logger

        callback = CustomJS(args=dict(text=text, button=button), code=self.CALLBACK)
        self.tapTool = tapTool(callback=callback)

    def addToPlot(self, plot):
        plot.add_tools(self.tapTool)
