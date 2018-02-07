from tools.referenceTool import ReferenceTool

from widgets.customButton import CustomButton
from customTapTool import CustomTapTool

from bokeh.models.widgets import TextInput
from bokeh.models.callbacks import CustomJS

class Reference:

    def __init__(self, logger, source, updateSources, peakPicking):
        self.logger = logger

        self.source = source
        self.updateSources = updateSources
        self.peakPicking = peakPicking

    def create(self):

        self.oldValue = self.newValue = None

        self.old = TextInput(title="Old Shift", placeholder="Old Shift", width=250, disabled=True)
        self.old.on_change('value', lambda attr, old, new: self.updateOldValue(new))

        self.new = TextInput(title="New Shift", placeholder="New Shift", width=250)
        self.new.on_change('value', lambda attr, old, new: self.updateNewValue(new))

        self.createButton()

        self.tool = CustomTapTool(self.logger, self.old, self.button, ReferenceTool)

    def createButton(self):
        self.button = CustomButton(label="Set Reference", button_type="success", width=500, error="Please select point using the reference tool.")
        self.button.on_click(self.updateData)
        buttonCallback = CustomJS(args=dict(button=self.button), code="""
            button.data = {};
        """)
        self.button.js_on_click(buttonCallback)

    def updateOldValue(self, value):
        self.oldValue = value

    def updateNewValue(self, value):
        self.newValue = value

    def updateData(self, position):

        try:
            oldValue = float(self.oldValue)
            newValue = float(self.newValue)
            n = oldValue - newValue

            newPPM = [point - n for point in self.source.data['ppm']]
            newData = list(self.source.data['data'])
            self.source.data = {
                'ppm': newPPM,
                'data': newData
            }

            self.updateDataSources(n)
        except ValueError:
            pass
        finally:
            self.oldValue = self.newValue = None
            self.old.value = self.new.value = ""

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

        # Update Chemical Shift Report
        self.peakPicking.updateChemicalShiftReport()

    def draw(self, plot):
        self.tool.addToPlot(plot)
        plot.toolbar.active_tap = None
