import pandas as pd
import os

from pymicruler.bp.BpRuler import BpRuler

# -------Quickstart-------

# Minimal program to (a) lookup breakpoints from species-compound pairs and (b) categorize
# isolates into susceptible, intermediate or resistant.
#
# Program execution takes a few seconds.

#
# INPUT DATA
#

working_directory = os.path.abspath(os.path.dirname(__file__))

resources_directory = os.path.join(working_directory, 'demo_resources')

path_to_mics = os.path.join(resources_directory, 'mic_demo_table.xlsx')
mics_df = pd.read_excel(path_to_mics)

results_directory = os.path.join(working_directory, 'demo_results')

path_to_processed_eucast = os.path.join(results_directory, 'processed_v_9.0_Breakpoint_Tables.xlsx')

#
# ANALYSIS
#

# Search breakpoints for species-compound pairs
bp = BpRuler()
bp_table = bp.run_breakpoint_query(path_to_processed_eucast, mics_df)
print(bp_table.head(10))

# Classify AST results into S/I/R
bp = BpRuler()
label_table = bp.run_sample_classification(path_to_processed_eucast, mics_df)
print(label_table.head(10))

# Find all resistance information that can be derived from the available data
bp = BpRuler()
full_table = bp.get_whole_resistance_phenotype(path_to_processed_eucast, mics_df)
print(full_table.head(10))



