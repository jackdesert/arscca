from decimal import Decimal
import math
import matplotlib.pyplot as plt
import numpy as np
import pdb

class Histogram:

    BIN_WIDTH = 2

    def __init__(self, drivers):
        # WARNING: drivers is a mutable list; don't change it
        self.raw_values = [driver.best_combined() for driver in drivers]

    def plot(self):
        values = [float(value) for value in self.raw_values if value < Decimal('inf')]
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


if __name__ == '__main__':
    from arscca.models.parser import Parser
    date = '2019-03-24'
    url = Parser.URLS[date]

    parser = Parser(date, url)
    parser.parse()

    histogram = Histogram(parser.drivers)
    histogram.plot()

