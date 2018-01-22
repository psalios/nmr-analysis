import gc
import os
from flask import Flask, request
from multiprocessing import Process

from createPlot import *
from logger import *

app = Flask(__name__)
logger = get_logger()

@app.route('/spectrum', methods=['POST'])
def spectrum():
  logger.info("Spectrum requested")
  path = request.form['path']
  fidLocation = request.form['fidLocation']
  spectrumLocation = request.form['spectrumLocation']
  contour_start = request.form['contour_start']

  logger.info("Parsing experiment data")
  dic1, data1 = ng.bruker.read(path)
  dic, data = ng.bruker.read_pdata(path+'/pdata/1/')
  logger.info("Experiment data parsed successfully")

  if os.path.exists(path+'/pdata/1/1r'):
    logger.info("Generating 1D Spectrum for " + path)
    p = Process(target=plot1D,args=(dic1,data1,dic,data,fidLocation,spectrumLocation))
    p.start()
    p.join()
  else:
    logger.info("Generating 2D Spectrum for " + path)
    logger.info("Contour level: " + contour_start)
    hasRange = request.form['hasRange']
    if hasRange == 'True':
      xstart = request.form['xstart']
      xend = request.form['xend']
      ystart = request.form['ystart']
      yend = request.form['yend']
      logger.info("Spectrum range: (" + xstart + ", " + ystart + ") - (" + xend + ", " + yend + ")")
      p = Process(target=plot2D,args=(dic1,data,spectrumLocation,contour_start,xstart,xend,ystart,yend,hasRange))
      p.start()
      p.join()
    else:
      p = Process(target=plot2D,args=(dic1,data,spectrumLocation,contour_start,0,0,0,0,hasRange))
      p.start()
      p.join()
  logger.info("Spectrum generated successfully")

  gc.collect()
  return ""

if __name__ == '__main__':
  logger.info("Spectrum Viewer started")
  app.run(host="0.0.0.0", port=Properties.GetProperty("python-server.port"))
