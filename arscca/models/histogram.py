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
        self._raw_values = [driver.primary_score() for driver in drivers]
        self._digest = self._construct_digest()
        self.conformed_count = 0

    def plot(self):
        values = self._values_to_use()
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

    def _values_to_use(self):
        # store self.conformed so view knows whether to display caveat
        values, self.conformed_count = self._conformed_values(self._raw_values)
        return values

    # This method is a classmethod to facilitate easy testing
    @classmethod
    def _conformed_values(cls, passed_in_values):
        # Any values greater than twice the minimum value are reduces the the next
        # loweste value
        # Example:
        # [10, 11, 21] => [10, 11, 11]

        values = [float(value) for value in passed_in_values if value < Decimal('inf')]

        if not values:
            # Return early to avoid error when min([]) is called
            return values, 0

        values.sort()
        minimum = min(values)
        twice_the_minimum = 2 * minimum
        last_allowable = minimum
        conformed_count = 0

        for index, value in enumerate(values):
            if value <= twice_the_minimum:
                last_allowable = value
            else:
                values[index] = last_allowable
                conformed_count += 1

        return (values, conformed_count)



if __name__ == '__main__':
    from arscca.models.parser import Parser
    date = '2019-03-24'
    url = Parser.URLS[date]

    parser = Parser(date, url)
    parser.parse()

    histogram = Histogram(parser.drivers)
    histogram.plot()
    print(histogram.filename)

