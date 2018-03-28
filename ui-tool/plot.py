#!/usr/bin/python

from layouts.customRow import CustomRow

from widgets.customButton import CustomButton

from tools.fixedZoomOutTool import FixedZoomOutTool
from tools.fixedWheelZoomTool import FixedWheelZoomTool
from tools.customTapTool import CustomTapTool
from tools.customBoxSelectTool import CustomBoxSelectTool
from tools.horizontalBoxZoomTool import HorizontalBoxZoomTool

from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models.annotations import BoxAnnotation
from bokeh.models.callbacks import CustomJS
from bokeh.models.glyphs import HBar
from bokeh.models.ranges import Range1d
from bokeh.models.sources import ColumnDataSource
from bokeh.io import curdoc

class Plot:

    WIDTH = 800
    HEIGHT = 600

    def __init__(self, shifts, multiplicities, deviations):

        self.shifts = shifts
        self.multiplicities = multiplicities
        self.deviations = deviations

        xr = Range1d(start=220, end=-20)
        yr = Range1d(start=0, end=1e10)

        self.plot = figure(x_axis_label="ppm", x_range=xr, y_range=yr, tools="save,reset", plot_width=self.WIDTH, plot_height=self.HEIGHT)

        # Remove grid from plot
        self.plot.xgrid.grid_line_color = None
        self.plot.ygrid.grid_line_color = None

        # Remove bokeh logo
        self.plot.toolbar.logo = None

        horizontalBoxZoomTool = HorizontalBoxZoomTool()
        self.plot.add_tools(horizontalBoxZoomTool)

        fixedZoomOutTool = FixedZoomOutTool(factor=0.4)
        self.plot.add_tools(fixedZoomOutTool)

        self.plot.extra_y_ranges['box'] = Range1d(start=0, end=0.1)
        self.selectionSource = ColumnDataSource(data=dict(left=[], right=[]), callback=CustomJS(code="""
            if ('data' in this.selected) {
                window.top.location.href = "http://localhost:8080?" + this.selected.data.query + "style=plot";
            }
        """))
        self.selectionSource.on_change('selected', lambda attr, old, new: self.delete(new['1d']['indices']))
        rect = HBar(
            left='left',
            right='right',
            y=0.5,
            height=1,
            line_alpha=0.3,
            fill_alpha=0.3,
            line_color="red",
            fill_color="red"
        )
        renderer = self.plot.add_glyph(self.selectionSource, rect)
        renderer.y_range_name = "box"

        removeTool = CustomTapTool()
        self.plot.add_tools(removeTool)
        self.plot.toolbar.active_tap = None

        callback = CustomJS(args=dict(), code="""
            /// get BoxSelectTool dimensions from cb_data parameter of Callback
            var geometry = cb_data['geometry'];

            var shift = (geometry['x0'] + geometry['x1']) / 2;
            var deviation = Math.abs(geometry['x1'] - shift);
            var query = cb_data['query'] + "shift%5B%5D=" + shift + '&multiplicity%5B%5D=m&deviation%5B%5D=' + deviation + '&style=plot';

            window.top.location.href = "http://localhost:8080?" + query;
        """)
        selectTool = CustomBoxSelectTool(
            tool_name="Select Area",
            dimensions = "width",
            callback = callback,
            query=self.paramsToQuery()
        )
        self.plot.add_tools(selectTool)

        self.initSelect()

        self.removeButton = CustomButton()

        curdoc().add_root(
            row(
                column(row(self.plot)),
                column(CustomRow(column(self.removeButton), hide=True))
            )
        )

    def paramsToQuery(self):
        query = ""
        for (shift, multiplicity, deviation) in zip(self.shifts, self.multiplicities, self.deviations):
            query += "shift%5B%5D={}&multiplicity%5B%5D={}&deviation%5B%5D={}&".format(shift, multiplicity, deviation)
        return query

    def initSelect(self):
        left, right = [], []
        for (shift, deviation) in zip(self.shifts, self.deviations):
            left.append(shift - deviation)
            right.append(shift + 2 * deviation)

        self.selectionSource.stream({
            'left': left,
            'right': right
        })

    def delete(self, ids):
        if ids:
            left = list(self.selectionSource.data['left'])
            right = list(self.selectionSource.data['right'])

            for i in ids:
                left.pop(i)
                right.pop(i)

                self.shifts.pop(i)
                self.multiplicities.pop(i)
                self.deviations.pop(i)

            self.selectionSource.data = {
                'left': left,
                'right': right
            }

            # Deselect all
            self.selectionSource.selected = {
                '0d': {'glyph': None, 'indices': []},
                '1d': {'indices': []},
                '2d': {'indices': {}},
                'data': {'query': self.paramsToQuery()}
            }

    def selectArea(self, dimensions):
        patch = {
            'left': [dimensions['x0']],
            'right': [dimensions['x1']]
        }
        self.selectionSource.stream(patch)
