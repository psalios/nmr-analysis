#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import ceil
import numpy as np

from common import *
from tools.bothDimensionsSelectTool import BothDimensionsSelectTool

from widgets.customButton import CustomButton

from bokeh.models.sources import ColumnDataSource
from bokeh.models.annotations import BoxAnnotation
from bokeh.models.widgets import Button, DataTable, TableColumn, Div, NumberFormatter, Select, TextInput, Paragraph
from bokeh.models.callbacks import CustomJS

class MultipletAnalysis:

    MULTIPLET_ERROR = 100000
    MULTIPLETS = {
        's': {'table': [1], 'sum': 1},
        'd': {'table': [1, 1], 'sum': 2},
        't': {'table': [1, 2, 1], 'sum': 3},
        'q': {'table': [1, 3, 3, 1], 'sum': 4},
        'p': {'table': [1, 4, 6, 4, 1], 'sum': 5},
        'h': {'table': [1, 5, 10, 10, 5, 1], 'sum': 6},
        'hept': {'table': [1, 6, 15, 20, 15, 6, 1], 'sum': 7},
        'dd': {'table': [[1, 1], [1, 1]], 'sum': 4},
        'td': {'table': [[1, 2, 1], [1, 1]], 'sum': 5},
        'ddt': {'table': [[1, 1], [1, 1], [1, 2, 1]], 'sum': 7},
        'ddd': {'table': [[1, 1], [1, 1], [1, 1], [1,1]], 'sum': 8}
    }

    def __init__(self, logger, dic, udic, pdata, dataSource, peakPicking, integration, reference):
        self.logger = logger

        self.dic = dic
        self.udic = udic
        self.pdata = pdata
        self.dataSource = dataSource

        self.peakPicking = peakPicking
        peakPicking.addObserver(self.recalculateAllMultipletsForPeaks)

        self.integration = integration

        reference.addObserver(lambda n: referenceObserver(self, n))

        self.sources = dict()

    def create(self):

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
        self.dataTable = DataTable(source=self.sources['table'], columns=columns, width=500)
        self.sources['table'].on_change('selected', lambda attr, old, new: self.rowSelect(new['1d']['indices']))
        self.sources['table'].on_change('data', lambda attr, old, new: self.updateMultipletReport())

        self.manual = CustomButton(label="Multiplet Analysis", button_type="primary", width=250, error="Please select area using the multiplet analysis tool.")
        self.manual.on_click(self.manualMultipletAnalysis)

        self.createTool()

        self.title = Div(text="<strong>Edit Multiplet:</strong>", width=500)
        self.name = TextInput(title="Name:", value="", placeholder="Name", width=150, disabled=True)
        self.name.on_change('value', lambda attr, old, new: self.manualChange('name', new))

        self.classes = Select(title="Class:", options=["m","s","d","t","q","p","h","hept","dd","td","ddt"], width=150, disabled=True)
        self.classes.on_change('value', lambda attr, old, new: self.manualChange('classes', new))

        self.integral = TextInput(title="Integral:", value="", placeholder="Integral", width=150, disabled=True)
        self.integral.on_change('value', lambda attr, old, new: self.changeIntegral(new))

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
            multiplet = ids[0]

            self.selected = multiplet

            # Enable options
            self.name.disabled = False
            self.name.value = self.sources['table'].data['name'][multiplet]

            self.classes.disabled = False
            self.classes.value = self.sources['table'].data['classes'][multiplet]

            self.integral.disabled = False
            self.integral.value = str(self.sources['table'].data['integral'][multiplet])

            self.delete.disabled = False
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
            patch['j'].append((pos, self.calcJ(ppm)))
        self.sources['table'].patch(patch)

    def recalculateAllMultipletsForIntegrals(self):
        data = self.sources['table'].data

        patch = dict(h=[])
        for pos, start, stop in zip(xrange(len(data['xStart'])), data['xStart'], data['xStop']):
            patch['h'].append((pos, ceil(self.integration.getIntegral(start, stop))))
        self.sources['table'].patch(patch)

    def manualMultipletAnalysis(self, dimensions):

        self.peakPicking.manualPeakPicking(dimensions)
        # Check if empty
        if not self.peakPicking.peaksIndices:
            return

        self.peakPicking.rowSelectFromPeaks(self.peakPicking.peaksIndices)

        integral = self.integration.calcIntegral(dimensions)

        peaks = [self.pdata[i] for i in self.peakPicking.peaksIndices]
        multiplet = self.predictMultiplet(peaks)

        ppm = sorted([self.dataSource.data['ppm'][i] for i in self.peakPicking.peaksIndices])
        data = {
            'xStart': [dimensions['x0']],
            'xStop':  [dimensions['x1']],
            'name':   ['A' if not self.sources['table'].data['name'] else chr(ord(self.sources['table'].data['name'][-1])+1)],
            'classes':  [multiplet],
            'j': [self.calcJ(ppm)],
            'h': [ceil(integral)],
            'integral': [integral],
            'peaks': [ppm],
            'top': [dimensions['y1']],
            'bottom': [dimensions['y0']]
        }

        # Add to DataTable
        self.sources['table'].stream(data)

    def calcJ(self, ppm):
        return round(abs(np.ediff1d(ppm).mean()) * getFrequency(self.udic) if len(ppm) > 1 else 0, 1)

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
            return self.checkMultiplicity(multiplet, peaks, None)

    def checkMultiplicity(self, multiplet, peaks, one):

        if not multiplet:
            return True

        for peak in peaks:
            if one is None:
                index = peaks.index(peak)
                peaks.remove(peak)
                if self.checkMultiplicity(list(multiplet)[1:], peaks, peak):
                    return True
                peaks.insert(index, peak)
            else:
                low = one * multiplet[0] - self.MULTIPLET_ERROR
                high = one * multiplet[0] + self.MULTIPLET_ERROR
                if peak >= low and peak <= high:
                    index = peaks.index(peak)
                    peaks.remove(peak)
                    if self.checkMultiplicity(list(multiplet)[1:], peaks, one):
                        return True
                    peaks.insert(index, peak)

        return False

    def updateMultipletReport(self):
        label = getLabel(self.udic)

        text = ""
        if label == "1H":
            data = self.sources['table'].data
            text = getMetadata(self.dic, self.udic) + " δ = " + ", ".join(
                ("{:0.2f}".format(np.median(peaks)) if classes != 'm' else "{:0.2f}-{:0.2f}".format(peaks[-1], peaks[0])) +
                " ({}, ".format(classes) +
                ("J={}, ".format(j) if j != 0 else "") +
                "{:d}H)".format(int(h))
                for (peaks, classes, j, h) in sorted(zip(data['peaks'], data['classes'], data['j'], data['h']), reverse=True)
            ) + "."
        elif label == "13C":
            text = self.peakPicking.getChemicalShiftReport()

        self.report.text = text

    def manualChange(self, key, new):
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

            integral = []
            for pos, val in zip(xrange(len(data)), data):
                integral.append((pos, val * ratio))
            self.sources['table'].patch(dict(integral=integral))

            self.integration.updateIntervals(ratio, self.integration.sources['table'].data)
        except:
            pass

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
        self.name.disabled = True
        self.classes.disabled = True
        self.integral.disabled = True
        self.delete.disabled = True

    def draw(self, plot):
        self.tool.addToPlot(plot)
