#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import ceil
import numpy as np

from customBoxSelect import CustomBoxSelect
from tools.multipletAnalysisSelectTool import MultipletAnalysisSelectTool

from widgets.customButton import CustomButton

from bokeh.models.sources import ColumnDataSource
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
        'dd': {'table': [[1, 1], [1, 1]], 'sum': 7},
        'td': {'table': [[1, 2, 1], [1, 1]], 'sum': 5},
        'ddt': {'table': [[1, 1], [1, 1], [1, 2, 1]], 'sum': 7}
    }

    def __init__(self, logger, pdata, dataSource, peakPicking, integration):
        self.logger = logger

        self.pdata = pdata
        self.dataSource = dataSource

        self.peakPicking = peakPicking
        self.peakPicking.sources['table'].on_change('data', lambda attr, old, new: self.recalculateAllMultipletsForPeaks())

        self.integration = integration
        self.integration.sources['table'].on_change('data', lambda attr, old, new: self.recalculateAllMultipletsForIntegrals())

        self.sources = dict()
        self.sources['select'] = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))

    def create(self):

        self.sources['table'] = ColumnDataSource(dict(xStart=[], xStop=[], name=[], classes=[], j=[], h=[], peak=[], top=[], bottom=[]))
        columns = [
            TableColumn(field="xStart", title="start", formatter=NumberFormatter(format="0.00")),
            TableColumn(field="xStop",  title="stop",  formatter=NumberFormatter(format="0.00")),
            TableColumn(field="name", title="Name"),
            TableColumn(field="classes", title="Class"),
            TableColumn(field="j", title="J"),
            TableColumn(field="h", title="H", formatter=NumberFormatter(format="0"))
        ]
        self.dataTable = DataTable(source=self.sources['table'], columns=columns, width=500)
        self.sources['table'].on_change('selected', lambda attr, old, new: self.rowSelect(new['1d']['indices']))
        self.sources['table'].on_change('data', lambda attr, old, new: self.updateMultipletReport())

        self.manual = CustomButton(label="Multiplet Analysis", button_type="primary", width=250, error="Please select area using the multiplet analysis tool.")
        self.manual.on_click(self.manualMultipletAnalysis)

        self.tool = CustomBoxSelect(self.logger, self.sources['select'], self.manual, selectTool=MultipletAnalysisSelectTool)

        self.createResetButton()

        self.title = Div(text="<strong>Edit Multiplet:</strong>", width=500)
        self.name = TextInput(title="Name:", value="", placeholder="Name", width=250, disabled=True)
        self.name.on_change('value', lambda attr, old, new: self.manualChange('name', new))

        self.classes = Select(title="Class:", options=["m","s","d","t","q","p","h","hept","dd","td","ddt"], width=250, disabled=True)
        self.classes.on_change('value', lambda attr, old, new: self.manualChange('classes', new))

        self.delete = Button(label="Delete Multiplet", button_type="danger", width=500, disabled=True)
        self.delete.on_click(self.deleteMultiplet)

        self.reportTitle = Div(text="<strong>Multiplet Report:</strong>")
        self.report = Paragraph(width=500)

    def rowSelect(self, ids):

        if len(ids) == 1:

            multiplet = ids[0]

            self.selected = multiplet

            # Enable options
            self.name.disabled = False
            self.name.value = self.sources['table'].data['name'][multiplet]

            self.classes.disabled = False
            self.classes.value = self.sources['table'].data['classes'][multiplet]

            self.delete.disabled = False

    def recalculateAllMultipletsForPeaks(self):
        data = self.sources['table'].data
        for pos, start, stop in zip(range(len(data['xStart'])), data['xStart'], data['xStop']):
            ppm = self.peakPicking.getPPMInSpace(start, stop)
            peaks = self.peakPicking.getPeaksInSpace(start, stop)

            multiplet = self.predictMultiplet(peaks)

            patch = {
                'classes': [(pos, multiplet)],
                'j': [(pos, self.calcJ(ppm))]
            }
            self.sources['table'].patch(patch)

    def recalculateAllMultipletsForIntegrals(self):
        data = self.sources['table'].data
        for pos, start, stop in zip(range(len(data['xStart'])), data['xStart'], data['xStop']):

            patch = {
                'h': [(pos, ceil(self.integration.getIntegral(start, stop)))]
            }
            self.sources['table'].patch(patch)

    def manualMultipletAnalysis(self, dimensions):
        # Clear selected area
        self.sources['select'].data = dict(x=[], y=[], width=[], height=[])

        self.peakPicking.manualPeakPicking(dimensions)
        # Check if empty
        if not self.peakPicking.peaksIndices:
            return

        self.peakPicking.rowSelectFromPeaks(self.peakPicking.peaksIndices)

        hydrogen = ceil(self.integration.manualIntegration(dimensions))
        self.integration.rowSelect([len(self.integration.sources['table'].data['xStart']) - 1])

        peaks = [self.pdata[i] for i in self.peakPicking.peaksIndices]
        multiplet = self.predictMultiplet(peaks)

        ppm = sorted([self.dataSource.data['ppm'][i] for i in self.peakPicking.peaksIndices])
        data = {
            'xStart': [dimensions['x0']],
            'xStop':  [dimensions['x1']],
            'name':   ['A' if not self.sources['table'].data['name'] else chr(ord(self.sources['table'].data['name'][-1])+1)],
            'classes':  [multiplet],
            'j': [self.calcJ(ppm)],
            'h': [hydrogen],
            'peak': [np.median(ppm)],
            'top': [dimensions['y1']],
            'bottom': [dimensions['y0']]
        }

        # Add to DataTable
        self.sources['table'].stream(data)

    def calcJ(self, ppm):
        return round(abs(np.ediff1d(ppm).mean()) * self.peakPicking.getFrequency() if len(ppm) > 1 else 0, 1)

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
                newPeaks = list(peaks)
                newPeaks.remove(peak)
                if self.checkMultiplicity(list(multiplet)[1:], newPeaks, peak):
                    return True
            else:
                low = one * multiplet[0] - self.MULTIPLET_ERROR
                high = one * multiplet[0] + self.MULTIPLET_ERROR
                if peak >= low and peak <= high:
                    newPeaks = list(peaks)
                    newPeaks.remove(peak)
                    if self.checkMultiplicity(list(multiplet)[1:], newPeaks, one):
                        return True

        return False

    def updateMultipletReport(self):
        label = self.peakPicking.getLabel()

        text = ""
        if label == "1H":
            data = self.sources['table'].data
            text = self.peakPicking.getMetadata() + " δ = " + ", ".join(
                "{:0.2f} ({}, ".format(peak, classes) +
                ("J={}, ".format(j) if j != 0 else "") +
                "{:d}H)".format(int(h))
                for (peak, classes, j, h) in sorted(zip(data['peak'], data['classes'], data['j'], data['h']), reverse=True)
            ) + "."
        elif label == "13C":
            text = self.peakPicking.getChemicalShiftReport()

        self.report.text = text

    def manualChange(self, key, new):
        patch = {
            key: [(self.selected, new)]
        }
        self.sources['table'].patch(patch)

    def deleteMultiplet(self):

        xStart  = list(self.sources['table'].data['xStart'])
        xStop   = list(self.sources['table'].data['xStop'])
        name    = list(self.sources['table'].data['name'])
        classes = list(self.sources['table'].data['classes'])
        j       = list(self.sources['table'].data['j'])
        h       = list(self.sources['table'].data['h'])
        peak    = list(self.sources['table'].data['peak'])
        top     = list(self.sources['table'].data['top'])
        bottom  = list(self.sources['table'].data['bottom'])

        xStart.pop(self.selected)
        xStop.pop(self.selected)
        name.pop(self.selected)
        classes.pop(self.selected)
        j.pop(self.selected)
        h.pop(self.selected)
        peak.pop(self.selected)
        top.pop(self.selected)
        bottom.pop(self.selected)

        self.sources['table'].data = {
            'xStart': xStart,
            'xStop': xStop,
            'name': name,
            'classes': classes,
            'j': j,
            'h': h,
            'peak': peak,
            'top': top,
            'bottom': bottom
        }
        self.deselectRows()

        self.disableOptions()

    def deselectRows(self):
        self.sources['table'].selected = {
            '0d': {'glyph': None, 'indices': []},
            '1d': {'indices': []},
            '2d': {'indices': {}}
        }

    def disableOptions(self):
        self.name.disabled = True
        self.classes.disabled = True
        self.delete.disabled = True

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

    def draw(self, plot):

        self.tool.addToPlot(plot)
        self.tool.addGlyph(plot, "#ffc700")
