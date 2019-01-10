import unittest
import os
import pandas as pd

from pymicruler.bp.EucastParser import EucastParser


class TestEucastParser(unittest.TestCase):

    def test_run_eucast_parser(self):
        ep = EucastParser()

        working_directory = os.path.abspath(os.path.dirname(__file__))

        inpath = os.path.join(working_directory, 'resources', 'parser_input.xlsx')
        result = ep.run_eucast_parser(inpath)

        outpath = os.path.join(working_directory, 'resources', 'parser_output.pkl')
        reference = pd.read_pickle(outpath)
        pd.testing.assert_frame_equal(reference, result)


if __name__ == '__main__':
    unittest.main()
