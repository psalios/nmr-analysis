import gc
import os

from createPlot import *
from logger import *

logger = get_logger()
logger.info("Spectrum Viewer started")

path = "/Users/mpsalios/Documents/sh/nmr-spectrum/data/1/"

logger.info("Parsing experiment data")
dic1, data1 = ng.bruker.read(path)
dic, data = ng.bruker.read_pdata(path+'/pdata/1/')
logger.info("Experiment data parsed successfully")

if os.path.exists(path+'/pdata/1/1r'):
    logger.info("Generating 1D Spectrum for " + path)
    plot1D(dic1, data1, dic, data)
    logger.info("Spectrum generated successfully")
