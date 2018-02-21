#!/usr/bin/python

import os
from logger import *
from plot import Plot
from bokeh.io import curdoc

logger = get_logger()
logger.info("Spectrum Viewer started")

with open("data/compounds/1.svg") as f:
    compound = f.read()
try:
    args = curdoc().session_context.request.arguments
    spectrum = int(args.get('spectrum')[0])
except:
    spectrum = 2

path = "data/{}/".format(spectrum)
if os.path.isdir(path):
    plot = Plot(logger, path, compound)
    plot.create()
    plot.draw()
