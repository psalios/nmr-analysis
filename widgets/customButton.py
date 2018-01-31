
from bokeh.core.properties import Int, Dict, String, Float
from bokeh.models.widgets import Button, AbstractButton

class CustomButton(AbstractButton):

    __implementation__ = "customButton.ts"
    clicks = Int(0)
    data = Dict(String, Float)

    def on_click(self, handler):
        self.on_change('clicks', lambda attr, old, new: handler(self.data))

    def js_on_click(self, handler):
        self.js_on_change('clicks', handler)
