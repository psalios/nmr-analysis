from customBoxSelect import CustomBoxSelect
from tools.multipletAnalysisSelectTool import MultipletAnalysisSelectTool

from widgets.customButton import CustomButton

from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Button, DataTable, TableColumn, Div, NumberFormatter, Select, TextInput
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
        self.integration = integration

        self.sources = dict()
        self.sources['select'] = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))

    def create(self):

        self.sources['table'] = ColumnDataSource(dict(xStart=[], xStop=[]))
        columns = [
            TableColumn(field="xStart", title="start", formatter=NumberFormatter(format="0.00")),
            TableColumn(field="xStop",  title="stop",  formatter=NumberFormatter(format="0.00")),
            # TableColumn(field="name", title="Name"),
            # TableColumn(field="class", title="Class"),
            # TableColumn(field="h", title="H")
        ]
        self.dataTable = DataTable(source=self.sources['table'], columns=columns, width=500)
        self.sources['table'].on_change('selected', lambda attr, old, new: self.rowSelect(new['1d']['indices']))

        self.manual = CustomButton(label="Multiplet Analysis", button_type="primary", width=250, error="Please select area using the multiplet analysis tool.")
        self.manual.on_click(self.manualMultipletAnalysis)

        self.tool = CustomBoxSelect(self.logger, self.sources['select'], self.manual, selectTool=MultipletAnalysisSelectTool)

        self.createResetButton()

        self.title = Div(text="<strong>Select Multiplet To Edit</strong>", width=500)
        self.name = TextInput(title="Name:", value="", placeholder="Name", width=250, disabled=True)
        self.classes = Select(title="Class:", options=["m","s","d","t","q","p","h","hept","dd","td","ddt"], width=250, disabled=True)
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

        peaks = [self.pdata[i] for i in self.peakPicking.peaksIndices]
        print(peaks)
        self.predictMultiplet(peaks)

        data = {
            'xStart': [dimensions['x0']],
            'xStop': [dimensions['x1']]
        }

        # Add to DataTable
        self.sources['table'].stream(data)

        # Clear selected area
        self.sources['select'].data = dict(x=[], y=[])

    def predictMultiplet(self, peaks):

        found = False
        for key, value in self.MULTIPLETS.iteritems():
            print(len(peaks), value['sum'])
            if len(peaks) == value['sum'] and self.checkMultiplet(value['table'], peaks):
                print(key)
                found = True
                self.classes.value = key
                break

        if not found:
            print("Not found")
            self.classes.value = "dd"

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
