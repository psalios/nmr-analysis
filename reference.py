from bokeh.models.widgets import Slider

class Reference:

    def __init__(self, logger, pdata, ppm_scale):
        self.logger = logger

        self.pdata = pdata
        self.ppm_scale = ppm_scale

    def create(self):

        minValue, maxValue = min(self.ppm_scale), max(self.ppm_scale)
        self.slider = Slider(start=minValue, end=maxValue, value=0.000, step=.001, title="Reference Change")
        self.slider.on_change('value', self.updateData)

    def updateData(self, attrname, old, new):
        diff = old - new
        print(diff)
