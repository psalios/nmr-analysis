#!/usr/bin/python

from bokeh.io import curdoc
from plot import Plot

args = curdoc().session_context.request.arguments

shifts = args.get('shift[]')
shifts = [float(shift) for shift in shifts] if shifts else []

multiplicities = args.get('multiplicity[]')
multiplicities = multiplicities if multiplicities else []

deviations = args.get('deviation[]')
deviations = [abs(float(deviation)) for deviation in deviations] if deviations else []

Plot(shifts, multiplicities, deviations)
