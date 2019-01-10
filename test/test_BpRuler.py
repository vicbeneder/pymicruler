import unittest
import pandas as pd
import os

from pymicruler.bp.BpRuler import BpRuler


class TestBpRuler(unittest.TestCase):
    def setUp(self):
        self.bpr = BpRuler()

        working_directory = os.path.abspath(os.path.dirname(__file__))

        in_path = os.path.join(working_directory, 'resources', 'ruler_input.xlsx')
        print('Test path', in_path)
        self.path_to_resource = os.path.join(
            working_directory, 'resources', 'processed_v_8.1_Breakpoint_Tables.xlsx')
        self.input = pd.read_excel(in_path)

    def test_run_bp_query(self):
        bp_table = self.bpr.run_breakpoint_query(self.path_to_resource, self.input)
        reference = pd.read_pickle('resources/breakpoint_query.pkl')
        pd.testing.assert_frame_equal(reference, bp_table)

    def test_classify_sample(self):
        label_table = self.bpr.run_sample_classification(self.path_to_resource, self.input)
        reference = pd.read_pickle('resources/label_query.pkl')
        pd.testing.assert_frame_equal(reference, label_table)

    def test_get_whole_resistance_phenotype(self):
        full_table = self.bpr.get_whole_resistance_phenotype(self.path_to_resource, self.input)
        reference = pd.read_pickle('resources/full_query.pkl')
        pd.testing.assert_frame_equal(reference, full_table)


if __name__ == '__main__':
    unittest.main()

