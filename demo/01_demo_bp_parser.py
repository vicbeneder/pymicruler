from pymicruler.bp.EucastParser import EucastParser

import os

# -------QUICKSTART-------

# Minimal program to parse a preprocessed EUCAST breakpoint table and write it to a file.
#
# Program execution takes approximately two minutes.

#
# INPUT
#

working_directory = os.path.abspath(os.path.dirname(__file__))

results_directory = os.path.join(working_directory, 'demo_results')

path_to_preprocessed_infile = os.path.join(
    working_directory, 'demo_resources', 'preprocessed_v_9.0_Breakpoint_Tables.xlsx')

path_to_parser_outfile = os.path.join(results_directory, 'processed_v_9.0_Breakpoint_Tables.xlsx')

#
# PARSING
#

# instantiate EUCAST parser object
ep = EucastParser()

# parse preprocessed EUCAST table; returns Pandas DataFrame
eucast_9_0 = ep.run_eucast_parser(path_to_preprocessed_infile)

print(eucast_9_0.head())

# write PandasDataFrame to Excel
if not os.path.exists(results_directory):
    os.makedirs(results_directory)

eucast_9_0.to_excel(path_to_parser_outfile, index=False)
