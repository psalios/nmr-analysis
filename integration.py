#!/usr/bin/python

import nmrglue as ng
import numpy as np

from customBoxSelect import CustomBoxSelect
from tools.integrationSelectTool import IntegrationSelectTool

from widgets.customButton import CustomButton

from bokeh.models.callbacks import CustomJS
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Button, DataTable, TableColumn, NumberFormatter, NumberEditor
from bokeh.models.glyphs import Rect

class Integration:

    def __init__(self, logger, pdata, dataSource):
        self.logger = logger

        self.pdata = pdata
        self.dataSource = dataSource

        self.sources = dict()
        self.sources['select'] = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))
        self.sources['integration'] = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))

        self.initIntegral = None

    def create(self):

        self.sources['table'] = ColumnDataSource(dict(xStart=[], xStop=[], top=[], bottom=[], integral=[]))
        columns = [
                TableColumn(field="xStart", title="start", editor=NumberEditor(step=0.01), formatter=NumberFormatter(format="0.00")),
                TableColumn(field="xStop", title="stop", editor=NumberEditor(step=0.01), formatter=NumberFormatter(format="0.00")),
                TableColumn(field="integral", title="integral", editor=NumberEditor(step=0.01), formatter=NumberFormatter(format="0.00"))
            ]
        self.dataTable = DataTable(source=self.sources['table'], columns=columns, width=500, editable=True)
        self.sources['table'].on_change('selected', lambda attr, old, new: self.rowSelect(new['1d']['indices']))
        self.sources['table'].on_change('data', lambda attr, old, new: self.changeData(old, new))

        self.manual = CustomButton(label="Manual Integration", button_type="primary", width=250, error="Please select area using the integration tool.")
        self.manual.on_click(self.manualIntegration)

        self.createResetButton()
        self.createDeselectButton()
        self.createDeleteButton()

        self.tool = CustomBoxSelect(self.logger, self.sources['select'], self.manual, selectTool=IntegrationSelectTool, dimensions="width")

    def changeData(self, old, new):
        diff = 1
        if len(old['integral']) == len(new['integral']):
            for o, n in zip(old['integral'], new['integral']):
                if o != n:
                    diff = n / o
                    break

        if diff != 1:
            self.initIntegral /= diff
            patch = {
                'integral': [(i, old['integral'][i] * diff) for i in xrange(len(old['integral']))]
            }
            self.sources['table'].patch(patch)

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

        return ratio

    def rowSelect(self, ids):

        maxBottom = min(max(self.sources['table'].data['bottom']), 0)
        minTop = max( min(self.sources['table'].data['top']), self.pdata.max())
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
        self.deselectButton = Button(label="Deselect all integrals", button_type="default", width=250)
        self.deselectButton.on_click(self.deselectData)

    def deselectData(self):
        self.sources['integration'].data = dict(x=[], y=[], width=[], height=[])
        self.deselectRows()

    def createDeleteButton(self):
        self.deleteButton = Button(label="Delete selected integrals", button_type="danger", width=250)
        self.deleteButton.on_click(self.deleteIntegrals)

    def deleteIntegrals(self):
        self.sources['integration'].data = dict(x=[], y=[], width=[], height=[])

        newStart = list(self.sources['table'].data['xStart'])
        newStop = list(self.sources['table'].data['xStop'])
        newTop = list(self.sources['table'].data['top'])
        newBottom = list(self.sources['table'].data['bottom'])
        newIntegral = list(self.sources['table'].data['integral'])

        ids = self.sources['table'].selected['1d']['indices']
        for i in ids:
            try:
                newStart.pop(i)
                newStop.pop(i)
                newTop.pop(i)
                newBottom.pop(i)
                newIntegral.pop(i)
            except IndexError:
                pass

        self.sources['table'].data = {
            'xStart': newStart,
            'xStop': newStop,
            'top': newTop,
            'bottom': newBottom,
            'integral': newIntegral
        }
        self.deselectRows()

    def deselectRows(self):
        self.sources['table'].selected = {
            '0d': {'glyph': None, 'indices': []},
            '1d': {'indices': []},
            '2d': {'indices': {}}
        }

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

        self.tool.addToPlot(plot)
        self.tool.addGlyph(plot, "#b3ffff")
