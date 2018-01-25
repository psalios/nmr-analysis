import nmrglue as ng
import numpy as np

from customBoxSelect import CustomBoxSelect

from widgets.customButton import CustomButton

from bokeh.models.callbacks import CustomJS
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Button, DataTable, TableColumn
from bokeh.models.glyphs import Rect

class Integration:

    def __init__(self, logger, pdata, ppm_scale, selectDataSource):
        self.logger = logger

        self.pdata = pdata
        self.ppm_scale = ppm_scale

        self.selectDataSource = selectDataSource
        self.integrationDataSource = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))

        self.initIntegral = None

    def create(self):

        self.source = ColumnDataSource(dict(start=[], stop=[], top=[], bottom=[], integral=[]))
        columns = [
                TableColumn(field="start", title="start"),
                TableColumn(field="stop", title="stop"),
                TableColumn(field="integral", title="integral")
            ]
        self.data_table = DataTable(source=self.source, columns=columns, width=500)
        self.source.on_change('selected', lambda attr, old, new: self.rowSelect(new))

        self.manual = CustomButton(label="Manual Integration", button_type="primary", width=250)
        self.manual.on_click(self.manualIntegration)

        self.createResetButton()
        self.createDeselectButton()

        self.tool = CustomBoxSelect(self.logger, self.selectDataSource, self.manual, "width")

    def manualIntegration(self, dimensions):

        points = [point for (point, pos) in zip(self.pdata, self.ppm_scale) if pos <= dimensions['x0'] and pos >= dimensions['x1']]
        integral = np.trapz(points, axis = 0)

        ratio = 1.0
        if self.initIntegral is None:
            self.initIntegral = integral
        else:
            ratio = integral / self.initIntegral

        # Update DataTable Values
        newStart = self.source.data['start'] + [dimensions['x0']]
        newStop = self.source.data['stop'] + [dimensions['x1']]
        newTop = self.source.data['top'] + [dimensions['y1']]
        newBottom = self.source.data['bottom'] + [dimensions['y0']]
        newIntegral = self.source.data['integral'] + [ratio]
        self.source.data = {
            'start': newStart,
            'stop': newStop,
            'top': newTop,
            'bottom': newBottom,
            'integral': newIntegral
        }

        # Clear selected area
        self.selectDataSource.data = dict(x=[], y=[], width=[], height=[])

    def rowSelect(self, rows):
        ids = rows['1d']['indices']

        maxBottom = max(self.source.data['bottom'])
        minTop = min(self.source.data['top'])
        tempHeight = minTop - maxBottom

        x, y, width, height = [], [], [], []
        for i in ids:
            sx0 = self.source.data['start'][i]
            sx1 = self.source.data['stop'][i]

            tempWidth = sx1 - sx0

            x.append(sx0 + tempWidth / 2)
            y.append(maxBottom + tempHeight / 2)
            width.append(tempWidth)
            height.append(tempHeight)

        self.integrationDataSource.data = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }

    def createResetButton(self):
        self.resetButton = Button(label="Clear Selected Area", button_type="default", width=250)
        resetButtonCallback = CustomJS(args=dict(source=self.selectDataSource, button=self.manual), code="""
            // get data source from Callback args
            var data = source.data;
            data['x'] = [];
            data['y'] = [];
            data['width'] = [];
            data['height'] = [];

            button.data = {};

            source.change.emit();
        """)
        self.resetButton.js_on_click(resetButtonCallback)

    def createDeselectButton(self):
        self.deselectButton = Button(label="Deselect all integrals", button_type="default", width=500)
        callback = CustomJS(args=dict(source=self.integrationDataSource), code="""
            // get data source from Callback args
            var data = source.data;
            data['x'] = [];
            data['y'] = [];
            data['width'] = [];
            data['height'] = [];

            source.change.emit();
        """)
        self.deselectButton.js_on_click(callback)

    def draw(self, plot):
        rect = Rect(
            x="x",
            y="y",
            width='width',
            height='height',
            fill_alpha=0.3,
            fill_color="#de5eff"
        )
        plot.add_glyph(self.integrationDataSource, rect, selection_glyph=rect, nonselection_glyph=rect)

        self.tool.addTool(plot)
        self.tool.addGlyph(plot, "#b3ffff")
