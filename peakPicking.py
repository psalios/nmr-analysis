import nmrglue as ng
from collections import OrderedDict

from widgets.manualPeakPickingButton import ManualPeakPickingButton

from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Button, DataTable, TableColumn
from bokeh.models.callbacks import CustomJS
from bokeh.models.markers import Circle
from bokeh.io import curdoc

class PeakPicking:

    def __init__(self, logger, pdata, ppm_scale, boxSelectDataSource):
        self.logger = logger

        self.pdata = pdata
        self.ppm_scale = ppm_scale
        self.boxSelectDataSource = boxSelectDataSource
        self.peaksDataSource = ColumnDataSource(data=dict(x=[], y=[]))

    def create(self):

        self.source = ColumnDataSource(dict(x=[], y=[]))
        columns = [
                TableColumn(field="x", title="ppm"),
                TableColumn(field="y", title="y"),
            ]
        self.data_table = DataTable(source=self.source, columns=columns, width=500)
        self.source.on_change('selected', lambda attr, old, new: self.rowSelect(new))

        self.auto = Button(label="Automatic Peak Picking", button_type="success", width=500)
        self.auto.on_click(self.autoPeakPicking)

        self.manual = ManualPeakPickingButton(label="Calculate Peaks", button_type="primary", width=250)
        self.manual.on_click(self.manualPeakPicking)

        self.createResetButton()

    def createResetButton(self):
        self.resetButton = Button(label="Clear Selected Area", button_type="default", width=250)
        resetButtonCallback = CustomJS(args=dict(source=self.boxSelectDataSource, button=self.manual), code="""
            // get data source from Callback args
            var data = source.data;
            data['x'] = [];
            data['y'] = [];
            data['width'] = [];
            data['height'] = [];

            button.data = {};

            source.change.emit();
        """)
        self.resetButton.js_on_click(resetButtonCallback);

    def autoPeakPicking(self):
        peaks = ng.peakpick.pick(self.pdata, 0)
        self.peaksIndices = [int(peak[0]) for peak in peaks]

        self.updateDataValues()


    def manualPeakPicking(self, dimensions):

        peaks = ng.peakpick.pick(self.pdata, dimensions['y0'] if dimensions['y0'] > 0 else 0)
        self.peaksIndices = [int(peak[0]) for peak in peaks]

        # Filter top
        self.peaksIndices = [i for i in self.peaksIndices if self.pdata[i] <= dimensions['y1']]
        # Filter left
        self.peaksIndices = [i for i in self.peaksIndices if self.ppm_scale[i] <= dimensions['x0']]
        # Filter right
        self.peaksIndices = [i for i in self.peaksIndices if self.ppm_scale[i] >= dimensions['x1']]

        self.updateDataValues()

        self.boxSelectDataSource.data = dict(x=[], y=[], width=[], height=[])

    def updateDataValues(self):
        # Update DataTable Values
        newData = list(OrderedDict.fromkeys(
            zip(
                self.source.data['x'] + [self.ppm_scale[i] for i in self.peaksIndices],
                self.source.data['y'] + [self.pdata[i] for i in self.peaksIndices]
            )
        ))
        newX, newY = zip(*newData)
        self.source.data = {
            'x': newX,
            'y': newY
        }

    def rowSelect(self, rows):
        ids = rows['1d']['indices']
        self.peaksDataSource.data = {
            'x': [self.source.data['x'][i] for i in ids],
            'y': [self.source.data['y'][i] for i in ids]
        }

    def draw(self, plot):
        circle = Circle(
            x="x",
            y="y",
            size=10,
            line_color="#ff0000",
            fill_color="#ff0000",
            line_width=1
        )
        plot.add_glyph(self.peaksDataSource, circle, selection_glyph=circle, nonselection_glyph=circle)
