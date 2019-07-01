from decimal import Decimal
import hashlib
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import pdb

class Histogram:

    BIN_WIDTH = 2
    WRITE_DIR = 'arscca/static/histograms'



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
        plt.title('Distribution of Scores')
        plt.ylabel('Drivers Per Bin')
        plt.xlabel('Time*')

        plt.axes().xaxis.set_major_locator(ticker.MultipleLocator(self.BIN_WIDTH * 2))
        plt.savefig(self.filename)

    @property
    def filename(self):
        return f'{self.WRITE_DIR}/{self._digest}.png'

    def _construct_digest(self):
        m = hashlib.sha256()
        assert self._raw_values

        # value comes in as Decimal()
        for value in self._raw_values:
            encoded = str(value).encode()
            m.update(encoded)
        return m.hexdigest()


if __name__ == '__main__':
    from arscca.models.parser import Parser
    date = '2019-03-24'
    url = Parser.URLS[date]

    parser = Parser(date, url)
    parser.parse()

    histogram = Histogram(parser.drivers)
    histogram.plot()
    print(histogram.filename)

