
from bokeh.models.callbacks import CustomJS
from bokeh.models.tools import BoxSelectTool
from bokeh.models.glyphs import Rect

class CustomBoxSelect:

    CALLBACK = """
        // get data source from Callback args
        var data = source.data;
        data['x'] = [];
        data['y'] = [];
        data['width'] = [];
        data['height'] = [];

        /// get BoxSelectTool dimensions from cb_data parameter of Callback
        var geometry = cb_data['geometry'];

        /// calculate Rect attributes
        var width = geometry['x1'] - geometry['x0'];
        var height = geometry['y1'] - geometry['y0'];
        var x = geometry['x0'] + width/2;
        var y = geometry['y0'] + height/2;

        /// update data source with new Rect attributes
        data['x'].push(x);
        data['y'].push(y);
        data['width'].push(width);
        data['height'].push(height);

        button.data = {
            x0: geometry['x0'],
            y0: geometry['y0'],
            x1: geometry['x1'],
            y1: geometry['y1']
        };

        // trigger update of data source
        source.change.emit();
    """

    def __init__(self, logger, source, button, dimensions="both"):
        self.logger = logger

        self.source = source

        callback = CustomJS(args=dict(source=source, button=button), code=self.CALLBACK)
        self.boxSelectTool = BoxSelectTool(dimensions=dimensions, callback=callback)

    def addTool(self, plot):
        plot.add_tools(self.boxSelectTool)

    def addGlyph(self, plot, fillColor="#ff0000"):
        rect = Rect(x='x',
                    y='y',
                    width='width',
                    height='height',
                    fill_alpha=0.3,
                    fill_color=fillColor)
        plot.add_glyph(self.source, rect, selection_glyph=rect, nonselection_glyph=rect)
