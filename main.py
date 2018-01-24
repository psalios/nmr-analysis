import gc
import os

from logger import *
from plot import Plot

logger = get_logger()
logger.info("Spectrum Viewer started")

path = "/Users/mpsalios/Documents/sh/nmr-spectrum/data/1/"

plot = Plot(logger, path)
plot.create()
plot.draw()
