#!/usr/bin/python

import os
from logger import *
from plot import Plot
from bokeh.io import curdoc

logger = get_logger()
logger.info("Spectrum Viewer started")

args = curdoc().session_context.request.arguments
try:
    spectrum = int(args.get('spectrum')[0])
except:
    spectrum = 2

path = "data/{}/".format(spectrum)
if os.path.isdir(path):
    plot = Plot(logger, path)
    plot.create()
    plot.draw()
