import nmrglue as ng
import numpy as np

from tools.fixedWheelZoomTool import FixedWheelZoomTool
from tools.horizontalBoxZoomTool import HorizontalBoxZoomTool
# from tools.resetTool import NewResetTool

from bokeh.layouts import row, column
from bokeh.core.properties import Float
from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.models import Range1d, Action, BoxZoomTool, CustomJS, HoverTool, DataTable, TableColumn, ColumnDataSource, BoxSelectTool, Rect
from bokeh.models.widgets import Button, Div
from bokeh.io import curdoc

WIDTH = 800
HEIGHT = 600

#Creates 1D Spectrum
def plot1D(dic1,data1,dic,data):
    data1 = ng.proc_base.di(data1)
    data1 = ng.proc_base.rev(data1)

    peaks = ng.peakpick.pick(data, 100000)
    npeaks = len(peaks)

    print(npeaks)
    peaksIndices = [int(peak[0]) for peak in peaks]

    # make ppm scale
    udic = ng.bruker.guess_udic(dic1, data)
    uc = ng.fileiobase.uc_from_udic(udic)
    ppm_scale = uc.ppm_scale()

    #Constants
    xr = Range1d(start=int(max(ppm_scale)+1),end=int(min(ppm_scale)-1))

    # create a new plot with a title and axis labels
    p = figure(x_axis_label='x', y_axis_label='y', x_range=xr, tools="pan,box_zoom,save,reset", plot_width=WIDTH, plot_height=HEIGHT)
    horizontalBoxZoomTool = HorizontalBoxZoomTool(dimensions="width")
    p.add_tools(horizontalBoxZoomTool)
    p.toolbar.active_drag = horizontalBoxZoomTool
    fixedWheelZoomTool = FixedWheelZoomTool(dimensions="height")
    p.add_tools(fixedWheelZoomTool)
    p.toolbar.active_scroll = fixedWheelZoomTool
    hover = HoverTool(tooltips="($x, $y)")
    p.add_tools(hover)

    manualPeakPickingSource = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))
    callback = CustomJS(args=dict(source=manualPeakPickingSource), code="""
        // get data source from Callback args
        var data = source.get('data');
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

        // trigger update of data source
        source.trigger('change');
    """)
    manualPeakPickingTool = BoxSelectTool(callback=callback, select_every_mousemove=True)
    p.add_tools(manualPeakPickingTool)
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    pline = p.line(ppm_scale, data, line_width=2)

    rect = Rect(x='x',
            y='y',
            width='width',
            height='height',
            fill_alpha=0.3,
            fill_color='#009933')
    pglyph = p.add_glyph(manualPeakPickingSource, rect, selection_glyph=rect, nonselection_glyph=rect)
    # p.circle(x = [ppm_scale[i] for i in peaksIndices], y = [data[i] for i in peaksIndices], size = 10)

    data = dict(
        x=[ppm_scale[i] for i in peaksIndices],
        y=[data[i] for i in peaksIndices],
    )
    source = ColumnDataSource(data)
    columns = [
            TableColumn(field="x", title="x"),
            TableColumn(field="y", title="y"),
        ]
    data_table = DataTable(source=source, columns=columns, width=400, height=280)

    par = Div(text="<strong>Peak Picking</strong>", width=200)
    button = Button(label="Calculate Peaks", button_type="primary")
    resetButton = Button(label="Clear Area", button_type="default")
    resetButtonCallback = CustomJS(args=dict(source=manualPeakPickingSource), code="""
        // get data source from Callback args
        var data = source.get('data');
        data['x'] = [];
        data['y'] = [];
        data['width'] = [];
        data['height'] = [];

        source.trigger('change');
    """)
    resetButton.js_on_click(resetButtonCallback);
    curdoc().add_root(row(column(p), column(row(par), row(column(button), column(resetButton)), row(data_table))))
