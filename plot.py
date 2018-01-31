import nmrglue as ng

from reference import Reference
from peakPicking import PeakPicking
from integration import Integration

from tools.fixedWheelZoomTool import FixedWheelZoomTool
from tools.horizontalBoxZoomTool import HorizontalBoxZoomTool

from bokeh.layouts import row, column, widgetbox
from bokeh.core.properties import Float
from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.models.callbacks import CustomJS
from bokeh.models.ranges import Range1d
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tools import HoverTool
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
                row(self.reference.slider)
            )

            peakPickingLayout = column(
                row(self.peakPicking.auto),
                row(
                    column(self.peakPicking.manual),
                    column(self.peakPicking.resetButton)
                ),
                row(self.peakPicking.data_table),
                row(self.peakPicking.deselectButton)
            )

            integrationLayout = column(
                row(
                    column(self.integration.manual),
                    column(self.integration.resetButton)
                ),
                row(self.integration.data_table),
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

        self.manualPeakPickingDataSource = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))
        self.integrationDataSource = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))

        self.reference = Reference(self.logger, self.pdata, self.ppm_scale)
        self.reference.create()

        self.peakPicking = PeakPicking(self.logger, self.pdata, self.ppm_scale, self.manualPeakPickingDataSource)
        self.peakPicking.create()
        self.peakPicking.draw(self.plot)

        self.integration = Integration(self.logger, self.pdata, self.ppm_scale, self.integrationDataSource)
        self.integration.create()
        self.integration.draw(self.plot)

        self.plot.line(self.ppm_scale, self.pdata, line_width=2)

    # make ppm scale
    def makePPMScale(self):
        udic = ng.bruker.guess_udic(self.dic, self.pdata)
        uc = ng.fileiobase.uc_from_udic(udic)
        self.ppm_scale = uc.ppm_scale()

    # create a new plot with a title and axis labels
    def newPlot(self):
        #Constants
        xr = Range1d(start=int(max(self.ppm_scale)+1),end=int(min(self.ppm_scale)-1))

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
        hover = HoverTool(tooltips="($x, $y)")
        self.plot.add_tools(hover)