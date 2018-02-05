import nmrglue as ng
import numpy as np

from customBoxSelect import CustomBoxSelect
from tools.integrationSelectTool import IntegrationSelectTool

from widgets.customButton import CustomButton

from bokeh.models.callbacks import CustomJS
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Button, DataTable, TableColumn, NumberFormatter
from bokeh.models.glyphs import Rect

class Integration:

    def __init__(self, logger, dataSource):
        self.logger = logger

        self.dataSource = dataSource

        self.sources = dict()
        self.sources['select'] = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))
        self.sources['integration'] = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))

        self.initIntegral = None

    def create(self):

        self.sources['table'] = ColumnDataSource(dict(xStart=[], xStop=[], top=[], bottom=[], integral=[]))
        columns = [
                TableColumn(field="xStart", title="start", formatter=NumberFormatter(format="0.00")),
                TableColumn(field="xStop", title="stop", formatter=NumberFormatter(format="0.00")),
                TableColumn(field="integral", title="integral", formatter=NumberFormatter(format="0.00"))
            ]
        self.dataTable = DataTable(source=self.sources['table'], columns=columns, width=500)
        self.sources['table'].on_change('selected', lambda attr, old, new: self.rowSelect(new))

        self.manual = CustomButton(label="Manual Integration", button_type="primary", width=250, error="Please select area using the integration tool.")
        self.manual.on_click(self.manualIntegration)

        self.createResetButton()
        self.createDeselectButton()

        self.tool = CustomBoxSelect(self.logger, self.sources['select'], self.manual, selectTool=IntegrationSelectTool, dimensions="width")

    def manualIntegration(self, dimensions):

        points = [point for (point, pos) in zip(self.dataSource.data['data'], self.dataSource.data['ppm']) if pos <= dimensions['x0'] and pos >= dimensions['x1']]
        integral = np.trapz(points, axis = 0)

        ratio = 1.0
        if self.initIntegral is None:
            self.initIntegral = integral
        else:
            ratio = integral / self.initIntegral

        # Update DataTable Values
        newStart = self.sources['table'].data['xStart'] + [dimensions['x0']]
        newStop = self.sources['table'].data['xStop'] + [dimensions['x1']]
        newTop = self.sources['table'].data['top'] + [dimensions['y1']]
        newBottom = self.sources['table'].data['bottom'] + [dimensions['y0']]
        newIntegral = self.sources['table'].data['integral'] + [ratio]
        self.sources['table'].data = {
            'xStart': newStart,
            'xStop': newStop,
            'top': newTop,
            'bottom': newBottom,
            'integral': newIntegral
        }

        # Clear selected area
        self.sources['select'].data = dict(x=[], y=[], width=[], height=[])

    def rowSelect(self, rows):
        ids = rows['1d']['indices']

        maxBottom = max(self.sources['table'].data['bottom'])
        minTop = min(self.sources['table'].data['top'])
        tempHeight = minTop - maxBottom

        x, y, width, height = [], [], [], []
        for i in ids:
            sx0 = self.sources['table'].data['xStart'][i]
            sx1 = self.sources['table'].data['xStop'][i]

            tempWidth = sx1 - sx0

            x.append(sx0 + tempWidth / 2)
            y.append(maxBottom + tempHeight / 2)
            width.append(tempWidth)
            height.append(tempHeight)

        self.sources['integration'].data = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }

    def createResetButton(self):
        self.resetButton = Button(label="Clear Selected Area", button_type="default", width=250)
        resetButtonCallback = CustomJS(args=dict(source=self.sources['select'], button=self.manual), code="""
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
        self.deselectButton.on_click(self.deselectData)

    def deselectData(self):
        self.sources['integration'].data = dict(x=[], y=[], width=[], height=[])

    def draw(self, plot):
        rect = Rect(
            x="x",
            y="y",
            width='width',
            height='height',
            fill_alpha=0.3,
            fill_color="#de5eff"
        )
        plot.add_glyph(self.sources['integration'], rect, selection_glyph=rect, nonselection_glyph=rect)

        self.tool.addTool(plot)
        self.tool.addGlyph(plot, "#b3ffff")
