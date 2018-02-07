from customBoxSelect import CustomBoxSelect
from tools.multipletAnalysisSelectTool import MultipletAnalysisSelectTool

from widgets.customButton import CustomButton

from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Button
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

        self.manual = CustomButton(label="Multiplet Analysis", button_type="primary", width=250, error="Please select area using the multiplet analysis tool.")
        self.manual.on_click(self.manualMultipletAnalysis)

        self.tool = CustomBoxSelect(self.logger, self.sources['select'], self.manual, selectTool=MultipletAnalysisSelectTool)

        self.createResetButton()

    def manualMultipletAnalysis(self, dimensions):
        self.peakPicking.manualPeakPicking(dimensions)

        print(self.peakPicking.peaksIndices)

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
