#!/usr/bin/python

import nmrglue as ng
import hashlib

from common import *
from reference import Reference
from peakPicking import PeakPicking
from integration import Integration
from multipletAnalysis import MultipletAnalysis
from spectrumDB import SpectrumDB

from layouts.customRow import CustomRow

from tools.customToolbar import CustomToolbar
from tools.fixedWheelZoomTool import FixedWheelZoomTool
from tools.fixedZoomOutTool import FixedZoomOutTool
from tools.horizontalBoxZoomTool import HorizontalBoxZoomTool
from tools.measureJTool import MeasureJTool

from bokeh.layouts import row, column
from bokeh.plotting import figure
from bokeh.models.callbacks import CustomJS
from bokeh.models.ranges import Range1d
from bokeh.models.sources import ColumnDataSource
from bokeh.models.glyphs import Text
from bokeh.models.tools import HoverTool
from bokeh.models.widgets.panels import Tabs, Panel
from bokeh.models.widgets.markups import Div
from bokeh.io import curdoc

class Plot:

    WIDTH = 800
    HEIGHT = 600

    def __init__(self, logger, path, compound):
        self.logger = logger

        self.logger.info("Parsing experiment data")
        self.dic, _ = ng.bruker.read(path)
        _, self.pdata = ng.bruker.read_pdata("{}/pdata/1/".format(path))
        self.logger.info("Experiment data parsed successfully")

        self.compound = compound
        self.id = SpectrumDB.Create(hashlib.sha256(self.pdata.tostring()).hexdigest())

    def draw(self):
        try:

            referenceLayout = column(
                row(
                    column(self.reference.old),
                    column(self.reference.new)
                ),
                row(self.reference.button)
            )

            peakPickingLayout = column(
                CustomRow(
                    column(self.peakPicking.manual),
                    column(self.peakPicking.peak),
                    hide=True
                ),
                row(self.peakPicking.dataTable),
                row(
                    column(self.peakPicking.deselectButton),
                    column(self.peakPicking.deleteButton)
                ),
                row(self.peakPicking.chemicalShiftReportTitle),
                row(self.peakPicking.chemicalShiftReport)
            )

            integrationLayout = column(
                CustomRow(
                    column(self.integration.manual),
                    hide=True
                ),
                row(self.integration.dataTable),
                row(
                    column(self.integration.deselectButton),
                    column(self.integration.deleteButton)
                )
            )

            multipletManagerLayout = column(
                CustomRow(
                    column(self.multipletAnalysis.manual),
                    hide=True
                ),
                row(self.multipletAnalysis.dataTable),
                row(self.multipletAnalysis.title),
                row(
                    column(self.multipletAnalysis.name),
                    column(self.multipletAnalysis.classes),
                    column(self.multipletAnalysis.integral)
                ),
                row(self.multipletAnalysis.delete),
                row(self.multipletAnalysis.reportTitle),
                row(self.multipletAnalysis.report)
            )

            referenceTab = Panel(child=referenceLayout, title="Reference")
            peakPickingTab = Panel(child=peakPickingLayout, title="Peak Picking")
            integrationTab = Panel(child=integrationLayout, title="Integration")
            multipletAnalysisTab = Panel(child=multipletManagerLayout, title="Multiplet Analysis")

            callback = CustomJS(args=dict(
                referenceTool=self.reference.tool,
                peakPickingManualTool=self.peakPicking.manualTool,
                peakPickingByPeakTool=self.peakPicking.peakTool,
                integrationTool=self.integration.tool,
                multipletAnalysisTool=self.multipletAnalysis.tool
                ), code="""
                switch(this.active) {
                case 0:
                    referenceTool.active = true;
                    break;
                case 1:
                    if (!peakPickingByPeakTool.active) {
                        peakPickingManualTool.active = true;
                    }
                    break;
                case 2:
                    integrationTool.active = true;
                    break;
                case 3:
                    multipletAnalysisTool.active = true;
                    break;
                }
            """)
            tabs = Tabs(tabs=[referenceTab, peakPickingTab, integrationTab, multipletAnalysisTab], width=500, callback=callback, id="tabs")

            curdoc().add_root(
                row(
                    column(
                        row(self.plot),
                        row(Div(text=self.compound, id="compoundContainer"))
                    ),
                    column(
                        row(tabs)
                    )
                )
            )
        except NameError:
            print("Please create plot first")

    def create(self):

        self.makePPMScale()

        self.newPlot()

        self.dataSource = ColumnDataSource(data=dict(ppm=self.ppmScale, data=self.pdata))

        self.reference = Reference(self.logger, self.dataSource)
        self.reference.create()
        self.reference.draw(self.plot)

        self.peakPicking = PeakPicking(self.logger, self.id, self.dic, self.udic, self.pdata, self.dataSource, self.reference)
        self.peakPicking.create()
        self.peakPicking.draw(self.plot)

        self.integration = Integration(self.logger, self.pdata, self.dataSource, self.reference)
        self.integration.create()
        self.integration.draw(self.plot)

        self.multipletAnalysis = MultipletAnalysis(self.logger, self.dic, self.udic, self.pdata, self.dataSource, self.peakPicking, self.integration, self.reference)
        self.multipletAnalysis.create()
        self.multipletAnalysis.draw(self.plot)

        self.createMeasureJTool()

        self.plot.line('ppm', 'data', source=self.dataSource, line_width=2)

    # make ppm scale
    def makePPMScale(self):
        self.udic = ng.bruker.guess_udic(self.dic, self.pdata)
        uc = ng.fileiobase.uc_from_udic(self.udic)
        self.ppmScale = uc.ppm_scale()

    # create a new plot with a title and axis labels
    def newPlot(self):
        #Constants
        xr = Range1d(start=int(max(self.ppmScale)+1),end=int(min(self.ppmScale)-1))

        self.plot = figure(x_axis_label='ppm', x_range=xr, toolbar=CustomToolbar(), tools="pan,save,reset", plot_width=self.WIDTH, plot_height=self.HEIGHT)

        # Remove grid from plot
        self.plot.xgrid.grid_line_color = None
        self.plot.ygrid.grid_line_color = None

        horizontalBoxZoomTool = HorizontalBoxZoomTool()
        self.plot.add_tools(horizontalBoxZoomTool)
        self.plot.toolbar.active_drag = horizontalBoxZoomTool

        fixedWheelZoomTool = FixedWheelZoomTool(dimensions="height")
        self.plot.add_tools(fixedWheelZoomTool)
        self.plot.toolbar.active_scroll = fixedWheelZoomTool

        fixedZoomOutTool = FixedZoomOutTool(factor=0.4)
        self.plot.add_tools(fixedZoomOutTool)

        hoverTool = HoverTool(tooltips="($x, $y)")
        self.plot.add_tools(hoverTool)

    def createMeasureJTool(self):
        source = ColumnDataSource(data=dict(x=[], y=[]))
        text = Text(x="x", y="y", text=[""], text_color="#000000")
        self.plot.add_glyph(source, text)

        measureJTool = MeasureJTool(text=text, textSource=source, frequency=getFrequency(self.udic))
        self.plot.add_tools(measureJTool)
