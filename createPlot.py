import nmrglue as ng
import numpy as np

from widgets.wheelZoomTool import FixedWheelZoomTool
from widgets.boxZoomTool import HorizontalBoxZoomTool
from widgets.resetTool import NewResetTool

from bokeh.resources import EMPTY
from bokeh.core.properties import Float
from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.models import Range1d, Action, BoxZoomTool, CustomJS, HoverTool

WIDTH = 800
HEIGHT = 600

#Creates 1D Spectrum
def plot1D(dic1,data1,dic,data):
  data1 = ng.proc_base.di(data1)
  data1 = ng.proc_base.rev(data1)

  #make ppm scale
  udic = ng.bruker.guess_udic(dic1, data)
  uc = ng.fileiobase.uc_from_udic(udic)
  ppm_scale = uc.ppm_scale()

  #Constants
  xr = Range1d(start=int(max(ppm_scale)+1),end=int(min(ppm_scale)-1))

  # create a new plot with a title and axis labels
  p = figure(x_axis_label='x', y_axis_label='y', x_range=xr, tools="pan,box_zoom,save,reset", plot_width=WIDTH, plot_height=HEIGHT)
  horizontalBoxZoomTool = HorizontalBoxZoomTool(dimensions=['width'])
  p.add_tools(horizontalBoxZoomTool)
  p.toolbar.active_drag = horizontalBoxZoomTool
  fixedWheelZoomTool = FixedWheelZoomTool(dimensions=["height"])
  p.add_tools(fixedWheelZoomTool)
  p.toolbar.active_scroll = fixedWheelZoomTool
  hover = HoverTool(tooltips="($x, $y)")
  p.add_tools(hover)
  p.xgrid.grid_line_color = None
  p.ygrid.grid_line_color = None

  # add a line renderer with legend and line thickness
  p.line(ppm_scale, data, line_width=2)

  show(p)
