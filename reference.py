from bokeh.models.widgets import TextInput

class Reference:

    def __init__(self, logger, source, updateSources):
        self.logger = logger

        self.source = source
        self.updateSources = updateSources

    def create(self):

        self.skip = False
        self.oldValue = 0.000
        self.textInput = TextInput(value="0.000", title="Reference")
        self.textInput.on_change('value', self.updateData)

    def updateData(self, attrname, old, new):
        if not self.skip and new:
            try:
                n = float(new)

                newPPM = [point - n for point in self.source.data['ppm']]
                newData = list(self.source.data['data'])
                self.source.data = {
                    'ppm': newPPM,
                    'data': newData
                }

                self.updateDataSources(n)

                self.oldValue = n
                self.skip = True
                self.textInput.value = "0.000"
            except ValueError:
                self.skip = True
                self.textInput.value= "0.000"
        elif self.skip:
            self.skip = False

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
