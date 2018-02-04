from tools.referenceTool import ReferenceTool

from widgets.customButton import CustomButton

from bokeh.models.widgets import TextInput
from bokeh.models.callbacks import CustomJS

class Reference:

    def __init__(self, logger, source, updateSources):
        self.logger = logger

        self.source = source
        self.updateSources = updateSources

    def create(self):

        self.value = 0.000
        self.textInput = TextInput(value="0.000", title="Reference Point", placeholder="Reference", width=550, disabled=True)
        self.textInput.on_change('value', lambda attr, old, new: self.updateValue(new))

        self.createButton()

        self.createTool()

    def createButton(self):
        self.button = CustomButton(label="Set Reference", button_type="success", width=500, error="Please select point using the reference tool.")
        self.button.on_click(self.updateData)
        buttonCallback = CustomJS(args=dict(button=self.button), code="""
            button.data = {};
        """)
        self.button.js_on_click(buttonCallback)

    def createTool(self):
        callback = CustomJS(args=dict(text=self.textInput, button=self.button), code="""

            /// get BoxSelectTool dimensions from cb_data parameter of Callback
            var geometry = cb_data['geometries'];

            var frame = this.plot_model.frame;
            var xm = frame.xscales['default'];

            var x = xm.invert(geometry.sx);
            button.data = {
                'x': x
            };
            text.value = x.toString();
        """)
        self.tool = ReferenceTool(callback=callback)

    def updateValue(self, value):
        self.value = value

    def updateData(self, position):

        try:
            n = float(self.value)

            newPPM = [point - n for point in self.source.data['ppm']]
            newData = list(self.source.data['data'])
            self.source.data = {
                'ppm': newPPM,
                'data': newData
            }

            self.updateDataSources(n)

            self.oldValue = n
            self.textInput.value = "0.000"
        except ValueError:
            self.textInput.value= "0.000"

    def updateDataSources(self, n):

        for source in self.updateSources:
            data = dict(source.data)

            if 'x' in data:
                data['x'] = [point - n for point in data['x']]
            if 'xStart' in data:
                data['xStart'] = [point - n for point in data['xStart']]
            if 'xStop' in data:
                data['xStop'] = [point - n for point in data['xStop']]
            source.data = data

    def draw(self, plot):
        plot.add_tools(self.tool)
        plot.toolbar.active_tap = None
