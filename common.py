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
