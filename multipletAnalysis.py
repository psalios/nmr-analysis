from customBoxSelect import CustomBoxSelect
from tools.multipletAnalysisSelectTool import MultipletAnalysisSelectTool

from widgets.customButton import CustomButton

from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Button, DataTable, TableColumn, Div, NumberFormatter, Select, TextInput
from bokeh.models.callbacks import CustomJS

class MultipletAnalysis:

    def __init__(self, logger, pdata, dataSource, peakPicking, integration):
        self.logger = logger

        self.pdata = pdata
        self.dataSource = dataSource

        self.peakPicking = peakPicking
        self.integration = integration

        self.sources = dict()
        self.sources['select'] = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))

    def create(self):

        self.sources['table'] = ColumnDataSource(dict(xStart=[], xStop=[]))
        columns = [
            TableColumn(field="xStart", title="start", formatter=NumberFormatter(format="0.00")),
            TableColumn(field="xStop",  title="stop",  formatter=NumberFormatter(format="0.00")),
        ]
        self.dataTable = DataTable(source=self.sources['table'], columns=columns, width=500)
        self.sources['table'].on_change('selected', lambda attr, old, new: self.rowSelect(new['1d']['indices']))

        self.manual = CustomButton(label="Multiplet Analysis", button_type="primary", width=250, error="Please select area using the multiplet analysis tool.")
        self.manual.on_click(self.manualMultipletAnalysis)

        self.tool = CustomBoxSelect(self.logger, self.sources['select'], self.manual, selectTool=MultipletAnalysisSelectTool)

        self.createResetButton()

        self.title = Div(text="<strong>Select Multiplet To Edit</strong>", width=500)
        self.name = TextInput(title="Name:", value="", placeholder="Name", width=250, disabled=True)
        self.classes = Select(title="Class:", options=["m","s","d","t","q","p","h"], width=250, disabled=True)
        self.delete = Button(label="Delete Multiplet", button_type="danger", width=500, disabled=True)

    def rowSelect(self, ids):

        if len(ids) == 1:

            # Enable options
            self.name.disabled = False
            self.classes.disabled = False
            self.delete.disabled = False

    def manualMultipletAnalysis(self, dimensions):
        self.peakPicking.manualPeakPicking(dimensions)
        self.peakPicking.rowSelectFromPeaks(self.peakPicking.peaksIndices)

        self.integration.manualIntegration(dimensions)
        self.integration.rowSelect([len(self.integration.sources['table'].data['xStart']) - 1])

        ppm = sorted([self.dataSource.data['ppm'][i] for i in self.peakPicking.peaksIndices], reverse=True)

        data = {
            'xStart': [dimensions['x0']],
            'xStop': [dimensions['x1']]
        }

        # Add to DataTable
        self.sources['table'].stream(data)

        # Clear selected area
        self.sources['select'].data = dict(x=[], y=[])

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
