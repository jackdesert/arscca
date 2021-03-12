from decimal import Decimal
import hashlib
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import pdb
from operator import itemgetter


class Histogram:

    POSSIBLE_BIN_WIDTHS = (
        1,
        2,
        4,
        5,
        10,
        20,
        25,
        40,
        50,
        60,
        75,
        100,
        120,
        125,
        150,
        175,
        200,
        250,
        300,
    )
    DEFAULT_BIN_WIDTH = 2
    WRITE_DIR = 'arscca/static/histograms'

    def __init__(self, drivers, dynamic_bin_width=False):
        # WARNING: drivers is a mutable list; don't change it
        self._raw_values = [driver.primary_score() for driver in drivers]
        self._digest = self._construct_digest()
        self.conformed_count = 0
        self.dynamic_bin_width = dynamic_bin_width

    def plot(self):
        values = self._values_to_use()
        if not values:
            return

        fixed_bin_width = None if self.dynamic_bin_width else self.DEFAULT_BIN_WIDTH
        bins = self._bins(values, fixed_bin_width)
        bin_width = bins[1] - bins[0]

        plt.hist(values, bins=bins, color='#dd2222', edgecolor='#665555', linewidth=0.8)
        plt.title('Distribution of Scores')
        plt.ylabel('Number of Drivers')
        plt.xlabel('Score*')

        plt.axes().xaxis.set_major_locator(ticker.MultipleLocator(bin_width * 2))
        plt.savefig(self.filename)
        plt.clf()

    # This method is a class method to facilitate easy testing
    @classmethod
    def _bins(cls, values, fixed_bin_width=0):
        min_value = min(values)
        max_value = max(values)
        num_values = len(values)

        if fixed_bin_width:
            bin_width = fixed_bin_width
        else:
            bin_width, _ = cls._bin_specification(min_value, max_value, num_values)

        left_edge, right_edge = 0, 0
        while left_edge + bin_width <= min_value:
            left_edge += bin_width

        # "If bins is a sequence, it defines the bin edges, including the left edge
        #  of the first bin and the right edge of the last bin"
        # see https://matplotlib.org/devdocs/api/_as_gen/matplotlib.pyplot.hist.html
        while right_edge <= max_value + bin_width:
            right_edge += bin_width

        bins = np.arange(left_edge, right_edge, bin_width)
        return bins

    # This method is a class method to facilitate easy testing
    @classmethod
    def _bin_specification(cls, min_value, max_value, num_values):
        # Sturges Rule
        # http://onlinestatbook.com/2/graphing_distributions/histograms.html
        expected_num_bins = round(1 + math.log(num_values, 2))
        expected_num_bins = math.ceil(expected_num_bins)

        span_required = max_value - min_value
        errors = {}

        for width in cls.POSSIBLE_BIN_WIDTHS:
            span = width * expected_num_bins
            error = abs(span - span_required)
            errors[width] = error

        # Sort dictionary by value
        errors_sorted = sorted(errors.items(), key=itemgetter(1))
        lowest_error = errors_sorted[0]
        width = lowest_error[0]

        # expected_num_bins is only returned to give more visibility into testing
        return (width, expected_num_bins)

    @property
    def filename(self):
        return f'{self.WRITE_DIR}/{self._digest}.png'

    def _construct_digest(self):
        m = hashlib.sha256()
        if not self._raw_values:
            raise AssertionError

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
    from arscca.models.dispatcher import Dispatcher
    date = '2021-03-14'
    url = ''
    live = False
    dispatcher = Dispatcher(date, url, live)
    dispatcher.compile()

    histogram = Histogram(dispatcher.drivers)
    histogram.plot()
    print(histogram.filename)
