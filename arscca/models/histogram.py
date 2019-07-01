from decimal import Decimal
import hashlib
import math
import matplotlib.pyplot as plt
import numpy as np
import pdb

class Histogram:

    BIN_WIDTH = 2

    def __init__(self, drivers):
        # WARNING: drivers is a mutable list; don't change it
        self._raw_values = [driver.best_combined() for driver in drivers]
        self._digest = self._construct_digest()

    def plot(self):
        values = [float(value) for value in self._raw_values if value < Decimal('inf')]
        min_value = min(values)
        max_value = max(values)
        left_edge = math.floor(min_value)
        right_edge = math.ceil(max_value)

        bins = np.arange(left_edge, right_edge, self.BIN_WIDTH)
        print(f'{len(values)} values')
        print(f'{len(bins)} bins')
        #hist = np.histogram(values, bins=bins)
        plt.hist(values, bins=bins)
        plt.savefig('/tmp/hi.png')

    def _construct_digest(self):
        m = hashlib.sha256()
        assert self._raw_values

        for value in self._raw_values:
            m.update(str(value))
        return m.hexdigest()

    def _filename(self):
        return f'{self._digest}.png'



if __name__ == '__main__':
    from arscca.models.parser import Parser
    date = '2019-03-24'
    url = Parser.URLS[date]

    parser = Parser(date, url)
    parser.parse()

    histogram = Histogram(parser.drivers)
    histogram.plot()

