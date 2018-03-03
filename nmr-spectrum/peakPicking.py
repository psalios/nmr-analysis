#!/usr/bin/python
# -*- coding: utf-8 -*-

import nmrglue as ng
import numpy as np
from collections import OrderedDict

from common import *
from observer import Observer
from spectrumDB import SpectrumDB

from customTapTool import CustomTapTool
from tools.bothDimensionsSelectTool import BothDimensionsSelectTool
from tools.peakByPeakTapTool import PeakByPeakTapTool
from widgets.customButton import CustomButton

from bokeh.models.sources import ColumnDataSource
from bokeh.models.annotations import BoxAnnotation
from bokeh.models.widgets import Button, DataTable, TableColumn, Div, Paragraph, NumberFormatter, TextInput
from bokeh.models.callbacks import CustomJS
from bokeh.models.markers import Circle

class PeakPicking(Observer):

    def __init__(self, logger, spectrumId, dic, udic, pdata, dataSource, reference):
        Observer.__init__(self, logger)
        self.logger = logger
        self.id = spectrumId

        self.dic = dic
        self.udic = udic
        self.pdata = pdata
        self.mpdata = np.array(map(lambda x: -x, pdata))
        self.dataSource = dataSource

        reference.addObserver(lambda n: referenceObserver(self, n))

        self.sources = dict()
        self.sources['peaks'] = ColumnDataSource(data=dict(x=[], y=[]))

    def create(self):

        self.sources['table'] = ColumnDataSource(dict(x=[], y=[]))
        columns = [
                TableColumn(field="x", title="ppm", formatter=NumberFormatter(format="0.00")),
                TableColumn(field="y", title="y", formatter=NumberFormatter(format="0.00"))
            ]
        self.dataTable = DataTable(source=self.sources['table'], columns=columns, reorderable=False, width=500)
        self.sources['table'].on_change('selected', lambda attr, old, new: self.rowSelect(new['1d']['indices']))
        self.sources['table'].on_change('data', lambda attr, old, new: self.dataChanged(old, new))

        self.manual = CustomButton(label="Manual Peaks", button_type="success", width=500, error="Please select area using the peak picking tool.")
        self.manual.on_click(self.manualPeakPicking)

        self.peak = CustomButton(label="Peak By Peak", button_type="primary", width=250, error="Please select area using the peak by peak tool.")
        self.peak.on_click(self.peakByPeakPicking)
        self.peakTool = CustomTapTool.Create(self.peak, tapTool=PeakByPeakTapTool, auto=True, id="peakByPeakTool")

        self.createManualTool()

        self.createDeselectButton()
        self.createDeleteButton()

        self.chemicalShiftReportTitle = Div(text="<strong>Chemical Shift Report</strong>" if getLabel(self.udic) == "13C" else "")
        self.chemicalShiftReport = Paragraph(text=self.getChemicalShiftReport(), width=500)

    def createManualTool(self):
        callback = CustomJS(args=dict(button=self.manual), code="""
            /// get BoxSelectTool dimensions from cb_data parameter of Callback
            var geometry = cb_data['geometry'];

            button.data = {
                x0: geometry['x0'],
                x1: geometry['x1'],
                y:  geometry['y']
            };

            // Callback to the backend
            button.clicks++;
        """)
        self.manualTool = BothDimensionsSelectTool(
            tool_name = "Peak Picking By Threshold",
            icon = "my_icon_peak_picking",
            callback = callback,
            id = "peakPickingByThresholdTool"
        )

    def dataChanged(self, old, new):

        added = list(set(new['x']) - set(old['x']))
        removed = list(set(old['x']) - set(new['x']))

        SpectrumDB.AddPeaks(self.id, added)
        SpectrumDB.RemovePeaks(self.id, removed)

        # Update Chemical Shift Report
        self.updateChemicalShiftReport()

    def updateChemicalShiftReport(self):
        self.chemicalShiftReport.text = self.getChemicalShiftReport()

    def getChemicalShiftReport(self):
        label = getLabel(self.udic)
        if label == "13C":
            return getMetadata(self.dic, self.udic) + " δ " + ", ".join("{:0.2f}".format(x) for x in [round(x, 2) for x in self.sources['table'].data['x']]) + "."
        else:
            return ""

    def createDeselectButton(self):
        self.deselectButton = Button(label="Deselect all peaks", button_type="default", width=250)
        self.deselectButton.on_click(lambda: deselectRows(self.sources['table']))

    def createDeleteButton(self):
        self.ids = []
        self.deleteButton = Button(label="Delete selected peaks", button_type="danger", width=250)
        self.deleteButton.on_click(self.deletePeaks)

    def deletePeaks(self):
        self.sources['peaks'].data = dict(x=[], y=[])

        newX = list(self.sources['table'].data['x'])
        newY = list(self.sources['table'].data['y'])

        ids = self.sources['table'].selected['1d']['indices']
        for i in sorted(ids, reverse=True):
            try:
                newX.pop(i)
                newY.pop(i)
            except IndexError:
                pass

        self.sources['table'].data = {
            'x': newX,
            'y': newY
        }
        deselectRows(self.sources['table'])

        self.notifyObservers()

    def manualPeakPicking(self, dimensions):

        # Positive Peaks
        self.peaksIndices = list(self.manualPeakPickingOnData(self.pdata, dimensions))

        # Negative Peaks
        self.peaksIndices.extend(self.manualPeakPickingOnData(self.mpdata, dimensions))

        if len(self.peaksIndices) > 0:
            self.updateDataValues({
                'x': [self.dataSource.data['ppm'][i] for i in self.peaksIndices],
                'y': [self.pdata[i] for i in self.peaksIndices]
            })
            self.notifyObservers()

    def manualPeakPickingOnData(self, data, dimensions):

        threshold = abs(dimensions['y'])
        if data.max() < threshold:
            return []

        peaks = ng.peakpick.pick(data, abs(dimensions['y']), algorithm="downward")

        peaksIndices = [int(peak[0]) for peak in peaks]
        # Filter left
        peaksIndices = [i for i in peaksIndices if self.dataSource.data['ppm'][i] <= dimensions['x0']]
        # Filter right
        peaksIndices = [i for i in peaksIndices if self.dataSource.data['ppm'][i] >= dimensions['x1']]
        return peaksIndices

    def peakByPeakPicking(self, dimensions):

        self.updateDataValues({
            'x': [dimensions['x']],
            'y': [dimensions['y']]
        })
        self.notifyObservers()

    def updateDataValues(self, data):
        # Update DataTable Values
        newData = list(OrderedDict.fromkeys(
            zip(
                self.sources['table'].data['x'] + data['x'],
                self.sources['table'].data['y'] + data['y']
            )
        ))
        newX, newY = zip(*sorted(newData, reverse=True))
        self.sources['table'].data = {
            'x': newX,
            'y': newY
        }

    def rowSelect(self, ids):
        self.sources['peaks'].data = {
            'x': [self.sources['table'].data['x'][i] for i in ids],
            'y': [self.sources['table'].data['y'][i] for i in ids]
        }

    def rowSelectFromPeaks(self, ids):
        self.sources['table'].selected = {
            '0d': {'glyph': None, 'indices': []},
            '1d': {'indices': [self.sources['table'].data['y'].index(self.pdata[i]) for i in ids]},
            '2d': {'indices': {}}
        }

    def getPeaksInSpace(self, start, stop):
        return [y for x, y in zip(self.sources['table'].data['x'], self.sources['table'].data['y']) if x <= start and x >= stop]

    def getPPMInSpace(self, start, stop):
        return [x for x in self.sources['table'].data['x'] if x <= start and x >= stop]

    def draw(self, plot):
        circle = Circle(
            x="x",
            y="y",
            size=10,
            line_color="#ff0000",
            fill_color="#ff0000",
            line_width=1
        )
        plot.add_glyph(self.sources['peaks'], circle, selection_glyph=circle, nonselection_glyph=circle)

        self.manualTool.addToPlot(plot)

        plot.add_tools(self.peakTool)
