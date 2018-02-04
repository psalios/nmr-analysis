from bokeh.core.properties import Int, Dict, String, Float, Instance
from bokeh.models.widgets import Button, AbstractButton

class CustomButton(AbstractButton):

    __implementation__ = "customButton.ts"
    clicks = Int(0)
    data = Dict(String, Float)
    error = String("An error occured. Please make sure for the correct usage of the functionality.")

    def on_click(self, handler):
        self.on_change('clicks', lambda attr, old, new: handler(self.data))

    def js_on_click(self, handler):
        self.js_on_change('clicks', handler)
