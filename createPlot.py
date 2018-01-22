import matplotlib
matplotlib.use('Agg')

import nmrglue as ng
import gc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm

from wheelZoomTool import FixedWheelZoomTool
from boxZoomTool import HorizontalBoxZoomTool
from resetTool import NewResetTool
from decreaseContourLevelTool import DecreaseContourLevelTool
from increaseContourLevelTool import IncreaseContourLevelTool

from bokeh.resources import EMPTY
from bokeh.core.properties import Float
from bokeh.embed import components
from bokeh.plotting import figure, output_file, save
from bokeh.models import Range1d, Action, BoxZoomTool, CustomJS

from jinja2 import Environment

WIDTH = 800
HEIGHT = 600

html_template = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        {{ EMPTY.render()|safe }}
        {{ bokeh_script|safe }}
    </head>
    <body>
    {{ plot | safe }}
    </body>
</html>
"""

#Creates 1D Spectrum
def plot1D(dic1,data1,dic,data,fidLocation,spectrumLocation):
  data1 = ng.proc_base.di(data1)
  data1 = ng.proc_base.rev(data1)

  #make ppm scale
  udic = ng.bruker.guess_udic(dic1, data)
  uc = ng.fileiobase.uc_from_udic(udic)
  ppm_scale = uc.ppm_scale()

  #Constants
  xr = Range1d(start=int(max(ppm_scale)+1),end=int(min(ppm_scale)-1))

  #create fid plot
  fid = figure(x_axis_label='x', y_axis_label='y',tools="pan,wheel_zoom,box_zoom,save,reset",plot_width=WIDTH,plot_height=HEIGHT)
  fid.xgrid.grid_line_color = None
  fid.ygrid.grid_line_color = None
  fid.line(ppm_scale,data1,line_width=2)
  script, div = components(fid)
  f = open(fidLocation,'w')
  f.write(div)
  f.write(script)
  f.close()

  # create a new plot with a title and axis labels
  p = figure(x_axis_label='x', y_axis_label='y', x_range=xr, tools="pan,box_zoom,save,reset", plot_width=WIDTH, plot_height=HEIGHT)
  horizontalBoxZoomTool = HorizontalBoxZoomTool(dimensions=['width'])
  p.add_tools(horizontalBoxZoomTool)
  p.toolbar.active_drag = horizontalBoxZoomTool
  fixedWheelZoomTool = FixedWheelZoomTool(dimensions=["height"])
  p.add_tools(fixedWheelZoomTool)
  p.toolbar.active_scroll = fixedWheelZoomTool
  p.xgrid.grid_line_color = None
  p.ygrid.grid_line_color = None

  # add a line renderer with legend and line thickness
  p.line(ppm_scale, data, line_width=2)

  # show the results
  script, div = components(p)
  content = Environment().from_string(html_template).render(bokeh_script=script, plot=div, EMPTY=EMPTY)
  with open(spectrumLocation, 'w') as f:
    f.write(content)

def plot2D(dic,data,spectrumLocation,contour_start,xstart,xend,ystart,yend,hasRange):
  # plot parameters
  cmap = matplotlib.cm.Blues_r           # contour map (colors to use for contours)
  contour_start = float(contour_start)   # contour level start value
  contour_num = 10                       # number of contour levels
  contour_factor = 1.20                  # scaling factor between contour levels

  cl = data.std() * contour_start * contour_factor ** np.arange(contour_num)
  # make ppm scales
  udic = ng.bruker.guess_udic(dic, data)
  uc_13c = ng.fileiobase.uc_from_udic(udic,1)
  ppm_13c = uc_13c.ppm_scale()
  ppm_13c_0, ppm_13c_1 = uc_13c.ppm_limits()
  udic = ng.bruker.guess_udic(dic, data)
  uc_15n = ng.fileiobase.uc_from_udic(udic,0)
  ppm_15n = uc_15n.ppm_scale()
  ppm_15n_0, ppm_15n_1 = uc_15n.ppm_limits()

  fig = plt.figure()
  ax = fig.add_subplot(111)
  # plot the contours
  newData = ax.contour(data, cl, cmap=cmap, extent=(ppm_13c_0, ppm_13c_1, ppm_15n_0, ppm_15n_1))
  plt.gca().invert_xaxis()
  plt.gca().invert_yaxis()

  xs = []
  ys = []
  for i in range(len(newData.allsegs)):
    for j in range(len(newData.allsegs[i])):
      newXS = []
      newYS = []
      for k in range(len(newData.allsegs[i][j])):
        newXS.append(newData.allsegs[i][j][k][0])
        newYS.append(newData.allsegs[i][j][k][1])
      xs.append(newXS)
      ys.append(newYS)
  colors = ["red" for i in range(len(xs))]
  if hasRange=='False':
    xr = Range1d(start=ppm_13c_0,end=ppm_13c_1)
    yr = Range1d(start=ppm_15n_0,end=ppm_15n_1)
  else:
    xr = Range1d(start=float(xstart),end=float(xend))
    yr = Range1d(start=float(ystart),end=float(yend))
  p = figure(plot_width=WIDTH, plot_height=HEIGHT, x_range=xr,y_range=yr, tools="pan,save")
  boxZoomTool = BoxZoomTool()
  p.add_tools(boxZoomTool)
  p.toolbar.active_drag = boxZoomTool
  resetTool = NewResetTool(xstart=ppm_13c_0,xend=ppm_13c_1,ystart=ppm_15n_0,yend=ppm_15n_1)
  p.add_tools(resetTool)
  decreaseContourLevelTool = DecreaseContourLevelTool()
  p.add_tools(decreaseContourLevelTool)
  increaseContourLevelTool = IncreaseContourLevelTool()
  p.add_tools(increaseContourLevelTool)
  p.multi_line(xs, ys,color=colors, line_width=0.5)

  p.x_range.callback = CustomJS(code="setXPlotRange(cb_obj['start'],cb_obj['end'])")
  p.y_range.callback = CustomJS(code="setYPlotRange(cb_obj['start'],cb_obj['end'])")

  #show the results
  output_file(spectrumLocation)
  save(p)

  #Clear matplotlib memory
  fig.clf()
  plt.close()
  del cl
  gc.collect()
