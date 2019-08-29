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
        if not values:
            return
        min_value = min(values)
        max_value = max(values)
        left_edge = math.floor(min_value)
        if left_edge % 2 == 1:
            left_edge -= 1
        right_edge = math.ceil(max_value) + self.BIN_WIDTH

        bins = np.arange(left_edge, right_edge, self.BIN_WIDTH)
        plt.hist(values, bins=bins, color='#dd2222', edgecolor='#665555', linewidth=0.8)
        plt.title('Distribution of Scores')
        plt.ylabel('Number of Drivers')
        plt.xlabel('Score*')

        plt.axes().xaxis.set_major_locator(ticker.MultipleLocator(self.BIN_WIDTH * 2))
        plt.savefig(self.filename)
        plt.clf()

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

