#!/bin/env python

'''
  currency_convert.py - Converts currency by multiplying the given field by the
  multiplier.  Currency will output in French locale.

  usage: currency_convert.py [-h] --field N [--multiplier N] [-i input]
                             [-o output] [--sane-csv]

  Currency Converter

  optional arguments:
    -h, --help      show this help message and exit
    --field N       Convert CSV field N
    --multiplier N  Multiply currency value by N for the current conversion rate
    -i input        Read from input file (or stdin)
    -o output       Write to output file (or stdout)
'''

import argparse
import locale
import re
import sys


class CSVWriter(object):
    '''
    This CSVWriter object is a naive, partial, implementation.  It just does
    a couple of things.
    '''

    def __init__(self, output_file):
        '''

        '''
        self.output_file = output_file

    def writerows(self, data):
        '''
        Loops over an array and calls writerow for each element.
        '''

        for row in data:
            self.writerow(row)

    def writerow(self, row):
        '''
        Loops over array and outputs a command separate list
        '''

        # As part of our naive CSV writer we check to see if , is part of
        # an element in the array and if so wrap the entire element in double quotes.
        output = []
        for item in row:
            if re.search(',', item):
                output.append("\"%s\"" % (item,))
            else:
                output.append(item)

        self.output_file.write(",".join(output)+"\n")


class NaiveCSV(object):
    '''
    This is a naive CSV implementation.  It doesn't handle all of the things that
    a proper CSV parser should handle.

    See: http://thomasburette.com/blog/2014/05/25/so-you-want-to-write-your-own-CSV-code/
    for all the reasons you don't want to write your own CSV parser.
    '''

    def reader(self, input_file):
        '''
        The reader interface is simple and just returns an array of parsed arrays.
        '''

        csv_data = []
        for line in input_file:
            # This regex is a little complicated, but basically it allows for
            # double or single quotes around strings with commas, and is
            # slightly less naive than a simple split(",").
            r = re.compile(r'''s*([^,"']+?|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*)\s*(?:,|$)''')
            fields = r.findall(line.rstrip())
            csv_data.append(fields)

        return csv_data

    def writer(self, output_file):
        '''
        The writer interface is a little more complicated and has some sub-functions.
        Return a reference to an object that will in turn handle everything that
        needs to be done.
        '''
        return CSVWriter(output_file)


def convert_currency(value, multiplier, loc='fr_FR', show_currency_symbol=False):
    '''
    Multiply value by multiplier and convert to given locale's monetary format.

    Defaults to French locale.

    Instructions unclear on if printing of the symbol should happen.  Seems like
    yes, but then ability to take output and feed it back in seems at odds with
    that instruction.  Ability to print symbol left of option, defaults to off.

    NOTE: in order to convert from a format that does non-decimal currency (ie commas)
    then this code needs to be updated slightly to properly parse the incoming currency.
    Exercise left for later when manager decides to go from French formatted Euros
    to USD.
    '''

    # If Franch formatted (ie uses commas) then need to call locale.atof or
    # something similar.

    computed_value = value * multiplier

    # Save the original local
    orig_loc = locale.getlocale()

    # Set the monetary category locale
    locale.setlocale(locale.LC_MONETARY, loc)

    # If printed this causes the symbol to be placed in front instead of behind
    locale._override_localeconv.update({'p_cs_precedes': 1, 'n_cs_precedes': 1})

    # Convert to local currency format
    converted = locale.currency(float(computed_value), symbol=show_currency_symbol,
                                grouping=True, international=True)

    # Revert the local back to original, might have been able to use resetlocale
    locale.setlocale(locale.LC_MONETARY, orig_loc)

    return converted


def main():

    parser = argparse.ArgumentParser(description='Currency Converter')

    parser.add_argument('--field', required=True, type=int, metavar='N',
                        help='Convert CSV field N')
    parser.add_argument('--multiplier', required=False, type=float,
                        metavar='N', default=1, help='Multiply currency value by N for the current conversion rate')
    parser.add_argument('-i', required=False, type=argparse.FileType('r'),
                        metavar='input', default=sys.stdin,
                        help='Read from input file (or stdin)')
    parser.add_argument('-o', required=False, type=argparse.FileType('w'),
                        metavar='output', default=sys.stdout,
                        help='Write to output file (or stdout)')

    parser.add_argument('--sane-csv', action='store_true', default=False)

    args = parser.parse_args()

    # Goal was to mimic csv behavior, without actually using csv module, but
    # also allow use of the csv module if wanted.
    if args.sane_csv:
        import csv
    else:
        csv = NaiveCSV()

    csvreader = csv.reader(args.i)
    csvwriter = csv.writer(args.o)

    for row in csvreader:
        field = row[args.field-1]
        row[args.field-1] = convert_currency(float(field), args.multiplier)
        csvwriter.writerow(row)


if __name__ == '__main__':
    main()
