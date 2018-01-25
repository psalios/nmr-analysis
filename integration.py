import nmrglue as ng
import numpy as np

from customBoxSelect import CustomBoxSelect

from widgets.customButton import CustomButton

from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets.buttons import Button

class Integration:

    def __init__(self, logger, pdata, ppm_scale, selectDataSource):
        self.logger = logger

        self.pdata = pdata
        self.ppm_scale = ppm_scale

        self.selectDataSource = selectDataSource

    def create(self):

        self.manual = CustomButton(label="Manual Integration", button_type="primary", width=250)
        self.manual.on_click(self.manualIntegration)

        self.createResetButton()

        self.tool = CustomBoxSelect(self.logger, self.selectDataSource, self.manual, "width")

    def manualIntegration(self, dimensions):
        print(dimensions)

        points = [point for point in self.pdata if point <= dimensions['x0'] and point >= dimensions['x1']]
        print(ng.integration.integrate(points))

    def createResetButton(self):
        self.resetButton = Button(label="Clear Selected Area", button_type="default", width=250)
        resetButtonCallback = CustomJS(args=dict(source=self.selectDataSource, button=self.manual), code="""
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

    def draw(self, plot):
        self.tool.addTool(plot)
        self.tool.addGlyph(plot, "#b3ffff")
