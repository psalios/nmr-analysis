import nmrglue as ng

from peakPicking import PeakPicking

from tools.fixedWheelZoomTool import FixedWheelZoomTool
from tools.horizontalBoxZoomTool import HorizontalBoxZoomTool

from bokeh.layouts import row, column, widgetbox
from bokeh.core.properties import Float
from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.models import Range1d, Action, BoxZoomTool, CustomJS, HoverTool, DataTable, TableColumn, ColumnDataSource, BoxSelectTool, Rect
from bokeh.models.widgets import Button, Div
from bokeh.io import curdoc

class Plot:

    WIDTH = 800
    HEIGHT = 600

    def __init__(self, logger, path):
        self.logger = logger

        self.logger.info("Parsing experiment data")
        self.dic, self.data = ng.bruker.read(path)
        _, self.pdata = ng.bruker.read_pdata(path+'/pdata/1/')
        self.logger.info("Experiment data parsed successfully")

    def draw(self):
        try:
            curdoc().add_root(
                row(
                    column(self.plot),
                    column(
                        row(self.par),
                        row(
                            column(self.peakPicking.button),
                            column(self.peakPicking.resetButton)
                        ),
                        row(self.peakPicking.data_table)
                    )
                )
            )
        except NameError:
            print("Please create plot first")

    def create(self):

        self.data = ng.proc_base.di(self.data)
        self.data = ng.proc_base.rev(self.data)

        self.makePPMScale()

        self.newPlot()

        self.boxSelectDataSource = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))

        self.peakPicking = PeakPicking(self.logger, self.pdata, self.ppm_scale, self.boxSelectDataSource)
        self.peakPicking.create()
        self.peakPicking.draw(self.plot)

        self.customBoxSelect()

        self.plot.line(self.ppm_scale, self.pdata, line_width=2)

        self.par = Div(text="<strong>Peak Picking</strong>", width=200)

    # create a new plot with a title and axis labels
    def newPlot(self):
        #Constants
        xr = Range1d(start=int(max(self.ppm_scale)+1),end=int(min(self.ppm_scale)-1))

        self.plot = figure(x_axis_label='x', y_axis_label='y', x_range=xr, tools="pan,box_zoom,save,reset", plot_width=self.WIDTH, plot_height=self.HEIGHT)

        # Remove grid from plot
        self.plot.xgrid.grid_line_color = None
        self.plot.ygrid.grid_line_color = None

        horizontalBoxZoomTool = HorizontalBoxZoomTool(dimensions="width")
        self.plot.add_tools(horizontalBoxZoomTool)
        self.plot.toolbar.active_drag = horizontalBoxZoomTool

        fixedWheelZoomTool = FixedWheelZoomTool(dimensions="height")
        self.plot.add_tools(fixedWheelZoomTool)
        self.plot.toolbar.active_scroll = fixedWheelZoomTool
        hover = HoverTool(tooltips="($x, $y)")
        self.plot.add_tools(hover)


    def makePPMScale(self):
        # make ppm scale
        udic = ng.bruker.guess_udic(self.dic, self.pdata)
        uc = ng.fileiobase.uc_from_udic(udic)
        self.ppm_scale = uc.ppm_scale()

    def customBoxSelect(self):
        callback = CustomJS(args=dict(source=self.boxSelectDataSource, button=self.peakPicking.button), code="""
            // get data source from Callback args
            var data = source.data;
            data['x'] = [];
            data['y'] = [];
            data['width'] = [];
            data['height'] = [];

            /// get BoxSelectTool dimensions from cb_data parameter of Callback
            var geometry = cb_data['geometry'];

            /// calculate Rect attributes
            var width = geometry['x1'] - geometry['x0'];
            var height = geometry['y1'] - geometry['y0'];
            var x = geometry['x0'] + width/2;
            var y = geometry['y0'] + height/2;

            /// update data source with new Rect attributes
            data['x'].push(x);
            data['y'].push(y);
            data['width'].push(width);
            data['height'].push(height);

            button.data = {
                x0: geometry['x0'],
                y0: geometry['y0'],
                x1: geometry['x1'],
                y1: geometry['y1']
            };

            // trigger update of data source
            source.change.emit();
        """)
        boxSelectTool = BoxSelectTool(callback=callback)
        self.plot.add_tools(boxSelectTool)

        rect = Rect(x='x',
                    y='y',
                    width='width',
                    height='height',
                    fill_alpha=0.3,
                    fill_color='#009933')
        self.plot.add_glyph(self.boxSelectDataSource, rect, selection_glyph=rect, nonselection_glyph=rect)
