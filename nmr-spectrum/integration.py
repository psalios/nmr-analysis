#!/usr/bin/python

import nmrglue as ng
import numpy as np

from common import *
from observer import Observer
from tools.customBoxSelectTool import CustomBoxSelectTool

from widgets.customButton import CustomButton

from bokeh.models.callbacks import CustomJS
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Button, DataTable, TableColumn, NumberFormatter, NumberEditor
from bokeh.models.glyphs import Rect

class Integration(Observer):

    def __init__(self, logger, pdata, dataSource, reference):
        Observer.__init__(self, logger)
        self.logger = logger

        self.pdata = pdata
        self.dataSource = dataSource

        reference.addObserver(lambda n: referenceObserver(self, n))

        self.sources = dict()
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

        self.createDeselectButton()
        self.createDeleteButton()

        callback = CustomJS(args=dict(button=self.manual), code="""
            /// get BoxSelectTool dimensions from cb_data parameter of Callback
            var geometry = cb_data['geometry'];

            button.data = {
                x0: geometry['x0'],
                x1: geometry['x1'],
                y0: geometry['y0'],
                y1: geometry['y1']
            };

            // Callback to the backend
            button.clicks++;
        """)
        self.tool = CustomBoxSelectTool(
            tool_name = "Integration",
            icon = "my_icon_integration",
            dimensions = "width",
            callback = callback,
            id = "integrationTool"
        )

    def changeData(self, old, new):
        self.checkRatio(old, new)

        self.checkRange(old, new, 'xStart')
        self.checkRange(old, new, 'xStop')

    def checkRatio(self, old, new):
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
            self.notifyObservers()

    def checkRange(self, old, new, key):
        if len(old[key]) == len(new[key]):
            for pos, o, n in zip(xrange(len(old[key])), old[key], new[key]):
                if o != n:
                    points = [point for (point, i) in zip(self.dataSource.data['data'], self.dataSource.data['ppm']) if i <= new['xStart'][pos] and i >= new['xStop'][pos]]
                    integral = np.trapz(points, axis = 0)
                    ratio = integral / self.initIntegral

                    patch = {
                        'integral': [(pos, ratio)]
                    }
                    self.sources['table'].patch(patch)
                    self.notifyObservers()
                    self.rowSelect([pos])


    def manualIntegration(self, dimensions):

        points = [point for (point, pos) in zip(self.dataSource.data['data'], self.dataSource.data['ppm']) if pos <= dimensions['x0'] and pos >= dimensions['x1']]
        integral = np.trapz(points, axis = 0)

        ratio = 1.0
        if self.initIntegral is None:
            self.initIntegral = integral
        else:
            ratio = integral / self.initIntegral

        # Update DataTable Values
        data = {
            'xStart': [dimensions['x0']],
            'xStop': [dimensions['x1']],
            'top': [dimensions['y1']],
            'bottom': [dimensions['y0']],
            'integral': [ratio]
        }
        self.sources['table'].stream(data)
        self.notifyObservers()

        return ratio

    def rowSelect(self, ids):

        maxBottom = min(max(self.sources['table'].data['bottom']) if self.sources['table'].data['bottom'] else 0, 0)
        minTop = max( min(self.sources['table'].data['top']) if self.sources['table'].data['top'] else 0, self.pdata.max())
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

    def createDeselectButton(self):
        self.deselectButton = Button(label="Deselect all integrals", button_type="default", width=250)
        self.deselectButton.on_click(lambda: deselectRows(self.sources['table']))

    def createDeleteButton(self):
        self.deleteButton = Button(label="Delete selected integrals", button_type="danger", width=250)
        self.deleteButton.on_click(self.deleteIntegrals)

    def deleteIntegrals(self):
        newStart = list(self.sources['table'].data['xStart'])
        newStop = list(self.sources['table'].data['xStop'])
        newTop = list(self.sources['table'].data['top'])
        newBottom = list(self.sources['table'].data['bottom'])
        newIntegral = list(self.sources['table'].data['integral'])

        ids = self.sources['table'].selected['1d']['indices']
        for i in sorted(ids, reverse=True):
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
        deselectRows(self.sources['table'])
        self.notifyObservers()

    def getIntegral(self, start, stop):
        return self.sources['table'].data['integral'][
            zip(self.sources['table'].data['xStart'], self.sources['table'].data['xStop']).index((start, stop))
        ]

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

        plot.add_tools(self.tool)
