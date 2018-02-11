#!/usr/bin/python

import nmrglue as ng
import hashlib

from reference import Reference
from peakPicking import PeakPicking
from integration import Integration
from multipletAnalysis import MultipletAnalysis
from spectrumDB import SpectrumDB

from tools.fixedWheelZoomTool import FixedWheelZoomTool
from tools.fixedZoomOutTool import FixedZoomOutTool
from tools.horizontalBoxZoomTool import HorizontalBoxZoomTool

from bokeh.layouts import row, column
from bokeh.plotting import figure
from bokeh.models.callbacks import CustomJS
from bokeh.models.ranges import Range1d
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.models.widgets.panels import Tabs, Panel
from bokeh.io import curdoc

class Plot:

    WIDTH = 800
    HEIGHT = 600

    def __init__(self, logger, path):
        self.logger = logger

        self.logger.info("Parsing experiment data")
        self.dic, _ = ng.bruker.read(path)
        _, self.pdata = ng.bruker.read_pdata("{}/pdata/1/".format(path))
        self.logger.info("Experiment data parsed successfully")

        self.id = SpectrumDB.Add(hashlib.sha256(self.pdata.tostring()).hexdigest())

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
                row(self.peakPicking.manual),
                row(self.peakPicking.peakInput),
                row(
                    column(self.peakPicking.peak),
                    column(self.peakPicking.resetButton)
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
                row(
                    column(self.integration.manual),
                    column(self.integration.resetButton)
                ),
                row(self.integration.dataTable),
                row(
                    column(self.integration.deselectButton),
                    column(self.integration.deleteButton)
                )
            )

            multipletManagerLayout = column(
                row(
                    column(self.multipletAnalysis.manual),
                    column(self.multipletAnalysis.resetButton)
                ),
                row(self.multipletAnalysis.dataTable),
                row(self.multipletAnalysis.title),
                row(
                    column(self.multipletAnalysis.name),
                    column(self.multipletAnalysis.classes)
                ),
                row(self.multipletAnalysis.delete),
                row(self.multipletAnalysis.reportTitle),
                row(self.multipletAnalysis.report)
            )

            referenceTab = Panel(child=referenceLayout, title="Reference")
            peakPickingTab = Panel(child=peakPickingLayout, title="Peak Picking")
            integrationTab = Panel(child=integrationLayout, title="Integration")
            multipletManagerTab = Panel(child=multipletManagerLayout, title="Multiplet Analysis")
            tabs = Tabs(tabs=[referenceTab, peakPickingTab, integrationTab, multipletManagerTab], width=500)

            curdoc().add_root(
                row(
                    column(self.plot),
                    column(tabs)
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

        self.peakPicking = PeakPicking(self.logger, self.dic, self.udic, self.pdata, self.dataSource, self.reference)
        self.peakPicking.create()
        self.peakPicking.draw(self.plot)

        self.integration = Integration(self.logger, self.pdata, self.dataSource, self.reference)
        self.integration.create()
        self.integration.draw(self.plot)

        self.multipletAnalysis = MultipletAnalysis(self.logger, self.pdata, self.dataSource, self.peakPicking, self.integration, self.reference)
        self.multipletAnalysis.create()
        self.multipletAnalysis.draw(self.plot)

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

        self.plot = figure(x_axis_label='ppm', y_axis_label='y', x_range=xr, tools="pan,save,reset", plot_width=self.WIDTH, plot_height=self.HEIGHT)

        # Remove grid from plot
        self.plot.xgrid.grid_line_color = None
        self.plot.ygrid.grid_line_color = None

        # Remove Bokeh logo
        self.plot.toolbar.logo = None

        horizontalBoxZoomTool = HorizontalBoxZoomTool(dimensions="width")
        self.plot.add_tools(horizontalBoxZoomTool)
        self.plot.toolbar.active_drag = horizontalBoxZoomTool

        fixedWheelZoomTool = FixedWheelZoomTool(dimensions="height")
        self.plot.add_tools(fixedWheelZoomTool)
        self.plot.toolbar.active_scroll = fixedWheelZoomTool

        fixedZoomOutTool = FixedZoomOutTool(factor=0.4)
        self.plot.add_tools(fixedZoomOutTool)

        hoverTool = HoverTool(tooltips="($x, $y)")
        self.plot.add_tools(hoverTool)
