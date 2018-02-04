import gc
import os

from logger import *
from plot import Plot

logger = get_logger()
logger.info("Spectrum Viewer started")

path = "data/3/"

plot = Plot(logger, path)
plot.create()
plot.draw()
