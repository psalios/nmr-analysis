#!/usr/bin/python

import os
from logger import *
from plot import Plot
from bokeh.io import curdoc

def readCompound(spectrum):
    with open("data/compounds/{}.svg".format(spectrum)) as f:
        return f.read();

logger = get_logger()
logger.info("Spectrum Viewer started")
try:
    args = curdoc().session_context.request.arguments
    spectrum = int(args.get('spectrum')[0])
except:
    spectrum = 1

compound = readCompound(spectrum)
path = "data/{}/".format(spectrum)
if os.path.isdir(path):
    plot = Plot(logger, spectrum, path, compound)
    plot.create()
    plot.draw()
