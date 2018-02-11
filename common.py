def referenceObserver(self, n):
    for source in self.sources.values():
        data = source.data

        patch = dict()
        if 'x' in data:
            patch['x'] = [(pos, point - n) for pos, point in zip(xrange(len(data['x'])), data['x'])]
        if 'xStart' in data:
            patch['xStart'] = [(pos, point - n) for pos, point in zip(xrange(len(data['xStart'])), data['xStart'])]
        if 'xStop' in data:
            patch['xStop'] = [(pos, point - n) for pos, point in zip(xrange(len(data['xStop'])), data['xStop'])]
        if 'peaks' in data:
            patch['peaks'] = [(pos, [point - n for point in peaks]) for pos, peaks in zip(xrange(len(data['peaks'])), data['peaks'])]
        source.patch(patch)

def getLabel(dic):
    return dic[0]['label']

def getSolvent(dic):
    return dic['acqus']['SOLVENT']

def getFrequency(dic):
    return int(round(dic[0]['obs'], 0))

def getFrequencyStr(dic):
    return str(getFrequency(dic)) + " MHz"

def getMetadata(dic, udic):
    return "{} NMR ({}, {})".format(getLabel(udic), getFrequencyStr(udic), getSolvent(dic))
