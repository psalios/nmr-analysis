import nmrglue as ng

from reference import Reference
from peakPicking import PeakPicking
from integration import Integration

from tools.fixedWheelZoomTool import FixedWheelZoomTool
from tools.horizontalBoxZoomTool import HorizontalBoxZoomTool
from tools.referenceTool import ReferenceTool

from bokeh.layouts import row, column, widgetbox
from bokeh.core.properties import Float
from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.models.callbacks import CustomJS
from bokeh.models.ranges import Range1d
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tools import HoverTool, TapTool
from bokeh.models.widgets import Button, Div, DataTable, TableColumn
from bokeh.models.widgets.panels import Tabs, Panel
from bokeh.io import curdoc

class Plot:

    WIDTH = 800
    HEIGHT = 600

    def __init__(self, logger, path):
        self.logger = logger

        self.logger.info("Parsing experiment data")
        self.dic, _ = ng.bruker.read(path)
        _, self.pdata = ng.bruker.read_pdata(path+'/pdata/1/')
        self.logger.info("Experiment data parsed successfully")

    def draw(self):
        try:

            referenceLayout = column(
                row(self.reference.textInput),
                row(self.reference.button)
            )

            peakPickingLayout = column(
                row(self.peakPicking.auto),
                row(
                    column(self.peakPicking.manual),
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
                row(self.integration.deselectButton)
            )

            referenceTab = Panel(child=referenceLayout, title="Reference")
            peakPickingTab = Panel(child=peakPickingLayout, title="Peak Picking")
            integrationTab = Panel(child=integrationLayout, title="Integration")
            tabs = Tabs(tabs=[referenceTab, peakPickingTab, integrationTab], width=500)

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

        self.peakPicking = PeakPicking(self.logger, self.dic, self.udic, self.pdata, self.dataSource)
        self.peakPicking.create()
        self.peakPicking.draw(self.plot)

        self.integration = Integration(self.logger, self.dataSource)
        self.integration.create()
        self.integration.draw(self.plot)

        sources = self.peakPicking.sources.values() + self.integration.sources.values()
        self.reference = Reference(self.logger, self.dataSource, sources, self.peakPicking)
        self.reference.create()
        self.reference.draw(self.plot)

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

        self.plot = figure(x_axis_label='ppm', y_axis_label='y', x_range=xr, tools="pan,box_zoom,save,reset", plot_width=self.WIDTH, plot_height=self.HEIGHT)

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

        hoverTool = HoverTool(tooltips="($x, $y)")
        self.plot.add_tools(hoverTool)
