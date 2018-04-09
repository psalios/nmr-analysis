#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

from common import *
from spectrumDB import SpectrumDB

from widgets.customButton import CustomButton
from tools.bothDimensionsSelectTool import BothDimensionsSelectTool

from bokeh.models.sources import ColumnDataSource
from bokeh.models.annotations import BoxAnnotation
from bokeh.models.widgets import Button, DataTable, TableColumn, Div, NumberFormatter, Select, TextInput, Paragraph
from bokeh.models.callbacks import CustomJS

class MultipletAnalysis:

    MULTIPLET_ERROR = 1000000
    MULTIPLETS = {
        's': {'table': [1], 'sum': 1, 'j': []},
        'd': {'table': [1, 1], 'sum': 2, 'j': [[0,1]]},
        't': {'table': [1, 2, 1], 'sum': 3, 'j': [[0,1]]},
        'q': {'table': [1, 3, 3, 1], 'sum': 4, 'j': [[0,1]]},
        'p': {'table': [1, 4, 6, 4, 1], 'sum': 5, 'j': [[0,1]]},
        'h': {'table': [1, 5, 10, 10, 5, 1], 'sum': 6, 'j': [[0,1]]},
        'hept': {'table': [1, 6, 15, 20, 15, 6, 1], 'sum': 7, 'j': [[0,1]]},
        'dd': {'table': [[1, 1], [1, 1]], 'sum': 4, 'j': [[0,1], [0,2]]},
        'ddd': {'table': [[1, 1], [1, 1], [1, 1], [1,1]], 'sum': 8, 'j': [[0,1], [0,2], [0,4]]},
        'dt': {'table': [[1, 2, 1], [1, 2, 1]], 'sum': 6, 'j': [[0,1], [0,3]]},
        'td': {'table': [1, 1, 2, 2, 1, 1], 'sum': 6, 'j': [[0,1], [0,2]]},
        'ddt': {'table': [[1, 2, 1], [1, 2, 1], [1, 2, 1], [1, 2, 1]], 'sum': 12, 'j': [[0,1], [0,3], [0,6]]}
    }

    def __init__(self, logger, spectrumId, dic, udic, pdata, dataSource, peakPicking, integration, reference):
        self.logger = logger
        self.id = spectrumId

        self.dic = dic
        self.udic = udic
        self.pdata = pdata
        self.dataSource = dataSource

        self.peakPicking = peakPicking
        peakPicking.addObserver(self.recalculateAllMultipletsForPeaks)

        self.integration = integration
        self.integration.addObserver(lambda ratio: self.updateIntervals(ratio, self.sources['table'].data['integral']))

        reference.addObserver(lambda n: referenceObserver(self, n))

        self.sources = dict()

    def create(self):

        self.oldData = dict(peaks=[], classes=[])
        self.sources['table'] = ColumnDataSource(dict(xStart=[], xStop=[], name=[], classes=[], j=[], h=[], integral=[], peaks=[], top=[], bottom=[]))
        columns = [
            TableColumn(field="xStart", title="start", formatter=NumberFormatter(format="0.00")),
            TableColumn(field="xStop",  title="stop",  formatter=NumberFormatter(format="0.00")),
            TableColumn(field="name", title="Name"),
            TableColumn(field="classes", title="Class"),
            TableColumn(field="j", title="J"),
            TableColumn(field="h", title="H", formatter=NumberFormatter(format="0")),
            TableColumn(field="integral", title="Integral", formatter=NumberFormatter(format="0.00"))
        ]
        self.dataTable = DataTable(source=self.sources['table'], columns=columns, reorderable=False, width=500)
        self.sources['table'].on_change('selected', lambda attr, old, new: self.rowSelect(new['1d']['indices']))
        self.sources['table'].on_change('data', lambda attr, old, new: self.dataChanged(new))

        self.manual = CustomButton(label="Multiplet Analysis", button_type="primary", width=250, error="Please select area using the multiplet analysis tool.")
        self.manual.on_click(self.manualMultipletAnalysis)

        self.createTool()

        self.title = Div(text="<strong>Edit Multiplet:</strong>", width=500)

        self.classes = Select(title="Class:", options=["m","s","d","t","q","p","h","hept","dd","ddd","dt","td","ddt"], width=100, disabled=True)
        self.classes.on_change('value', lambda attr, old, new: self.manualChange('classes', new))

        self.integral = TextInput(title="Integral:", value="", placeholder="Integral", width=175, disabled=True)
        self.integral.on_change('value', lambda attr, old, new: self.changeIntegral(new))

        self.j = TextInput(title='J-list:', value="", width=175, disabled=True)
        self.j.on_change('value', lambda attr, old, new: self.manualChange('j', new))

        self.delete = Button(label="Delete Multiplet", button_type="danger", width=500, disabled=True)
        self.delete.on_click(self.deleteMultiplet)

        self.reportTitle = Div(text="<strong>Multiplet Report:</strong>")
        self.report = Paragraph(width=500)

    def createTool(self):
        callback = CustomJS(args=dict(button=self.manual), code="""
            /// get BoxSelectTool dimensions from cb_data parameter of Callback
            var geometry = cb_data['geometry'];

            button.data = {
                x0: geometry['x0'],
                x1: geometry['x1'],
                y:  geometry['y'],
                y0: geometry['y0'],
                y1: geometry['y1']
            };

            // Callback to the backend
            button.clicks++;
        """)
        self.tool = BothDimensionsSelectTool(
            tool_name = "Multiplet Analysis",
            icon = "my_icon_multiplet_analysis",
            callback = callback,
            id = "multipletAnalysisTool"
        )

    def rowSelect(self, ids):

        if len(ids) == 1:
            self.selected = ids[0]

            # Enable options
            self.classes.disabled = False
            self.classes.value = self.sources['table'].data['classes'][self.selected]

            self.integral.disabled = False
            self.integral.value = str(self.sources['table'].data['integral'][self.selected])

            self.j.disabled = False
            self.j.value = self.sources['table'].data['j'][self.selected]

            self.delete.disabled = False

            self.peakPicking.selectByPPM(self.sources['table'].data['peaks'][self.selected])
        else:
            deselectRows(self.sources['table'])

    def recalculateAllMultipletsForPeaks(self):
        data = self.sources['table'].data

        patch = dict(classes=[], j=[])
        for pos, start, stop in zip(range(len(data['xStart'])), data['xStart'], data['xStop']):
            ppm = self.peakPicking.getPPMInSpace(start, stop)
            peaks = self.peakPicking.getPeaksInSpace(start, stop)

            multiplet = self.predictMultiplet(peaks)

            patch['classes'].append((pos, multiplet))
            patch['j'].append((pos, self.calcJ(ppm, multiplet)))
        self.sources['table'].patch(patch)

    def manualMultipletAnalysis(self, dimensions):

        self.peakPicking.manualPeakPicking(dimensions, notify=False)
        # Check if empty
        if not self.peakPicking.peaksIndices:
            return

        integral = round(self.integration.calcIntegral(dimensions), 3)

        peaks = [self.pdata[i] for i in self.peakPicking.peaksIndices]
        multiplet = self.predictMultiplet(peaks)

        ppm = sorted([self.dataSource.data['ppm'][i] for i in self.peakPicking.peaksIndices])
        data = {
            'xStart': [dimensions['x0']],
            'xStop':  [dimensions['x1']],
            'name':   ['A' if not self.sources['table'].data['name'] else chr(ord(self.sources['table'].data['name'][-1])+1)],
            'classes':  [multiplet],
            'j': [self.calcJ(ppm, multiplet)],
            'h': [round(integral)],
            'integral': [integral],
            'peaks': [ppm],
            'top': [dimensions['y1']],
            'bottom': [dimensions['y0']]
        }

        # Add to DataTable
        self.sources['table'].stream(data)

        # Select the multiplet in the table
        self.sources['table'].selected = {
            '0d': {'glyph': None, 'indices': []},
            '1d': {'indices': [len(self.sources['table'].data['xStart']) - 1]},
            '2d': {'indices': {}}
        }

    def calcJ(self, ppm, multiplet):
        if multiplet in self.MULTIPLETS:
            js = self.MULTIPLETS[multiplet]['j']

            calc = sorted([round(abs(ppm[j[0]] - ppm[j[1]]) * getFrequency(self.udic), 1) for j in js], reverse=True)
            return ', '.join(str(j) for j in calc) + ' Hz'
        return ""

    def predictMultiplet(self, peaks):

        for key, value in self.MULTIPLETS.iteritems():
            if len(peaks) == value['sum'] and self.checkMultiplet(value['table'], peaks):
                return key

        return "m"

    def checkMultiplet(self, multiplet, peaks):

        if not multiplet:
            return True

        # check list
        if isinstance(multiplet[0], list):
            return self.checkMultiplet(multiplet[0], peaks) and self.checkMultiplet(multiplet[1:], peaks)
        else:
            return self.checkMultiplicity(multiplet, peaks)

    def checkMultiplicity(self, multiplet, peaks):

        if not multiplet:
            return True

        for (m, peak) in zip(multiplet[1:], peaks[1:]):

            low = m * peaks[0] - self.MULTIPLET_ERROR
            high = m * peaks[0] + self.MULTIPLET_ERROR

            if peak < low or peak > high:
                return False

        return True

    def dataChanged(self, data):

        self.updateMultipletReport()

        label = getLabel(self.udic)
        if label == "1H":
            newData = [(np.median(peaks), c) for (peaks, c) in zip(data['peaks'], data['classes'])]
            oldData = [(np.median(peaks), c) for (peaks, c) in zip(self.oldData['peaks'], self.oldData['classes'])]

            added = list(set(newData) - set(oldData))
            removed = list(set(oldData) - set(newData))

            SpectrumDB.RemovePeaks(self.id, removed)
            SpectrumDB.AddPeaks(self.id, added)

            self.oldData = {
                'peaks': [i[0] for i in newData],
                'classes': [i[1] for i in newData]
            }

    def updateMultipletReport(self):
        label = getLabel(self.udic)

        text = ""
        if label == "1H":
            data = self.sources['table'].data
            text = getMetadata(self.dic, self.udic) + " δ = " + ", ".join(
                ("{:0.2f}".format(np.median(peaks)) if classes != 'm' else "{:0.2f}-{:0.2f}".format(peaks[-1], peaks[0])) +
                " ({}, ".format(classes) +
                ("J={}, ".format(j) if classes != 'm' and classes != 's' else "") +
                "{:d}H)".format(int(h))
                for (peaks, classes, j, h) in sorted(zip(data['peaks'], data['classes'], data['j'], data['h']), reverse=True) if h > 0
            ) + "."

        self.report.text = text

    def manualChange(self, key, new):
        if self.sources['table'].data[key][self.selected] != new:
            patch = {
                key: [(self.selected, new)]
            }
            self.sources['table'].patch(patch)

    def changeIntegral(self, new):
        try:
            new = float(new)

            data = self.sources['table'].data['integral']

            old = data[self.selected]
            ratio = new / old

            self.updateIntervals(ratio, data)

            self.integration.updateIntervals(ratio, self.integration.sources['table'].data)
        except:
            pass

    def updateIntervals(self, ratio, data):
        h, integral = [], []
        for pos, val in zip(xrange(len(data)), data):
            newIntegral = val * ratio
            h.append((pos, round(newIntegral)))
            integral.append((pos, newIntegral))
        self.sources['table'].patch(dict(h=h, integral=integral))

    def deleteMultiplet(self):

        xStart   = list(self.sources['table'].data['xStart'])
        xStop    = list(self.sources['table'].data['xStop'])
        name     = list(self.sources['table'].data['name'])
        classes  = list(self.sources['table'].data['classes'])
        j        = list(self.sources['table'].data['j'])
        h        = list(self.sources['table'].data['h'])
        integral = list(self.sources['table'].data['integral'])
        peaks    = list(self.sources['table'].data['peaks'])
        top      = list(self.sources['table'].data['top'])
        bottom   = list(self.sources['table'].data['bottom'])

        xStart.pop(self.selected)
        xStop.pop(self.selected)
        name.pop(self.selected)
        classes.pop(self.selected)
        j.pop(self.selected)
        h.pop(self.selected)
        integral.pop(self.selected)
        peaks.pop(self.selected)
        top.pop(self.selected)
        bottom.pop(self.selected)

        self.sources['table'].data = {
            'xStart': xStart,
            'xStop': xStop,
            'name': name,
            'classes': classes,
            'j': j,
            'h': h,
            'integral': integral,
            'peaks': peaks,
            'top': top,
            'bottom': bottom
        }
        deselectRows(self.sources['table'])

        self.disableOptions()

    def disableOptions(self):
        self.classes.disabled = True
        self.integral.disabled = True
        self.j.disabled = True
        self.delete.disabled = True

    def draw(self, plot):
        self.tool.addToPlot(plot)
