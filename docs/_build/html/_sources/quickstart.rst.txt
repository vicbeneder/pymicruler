.. _quickstart:
Quickstart
==========

After :ref:`installation` of the package, the analysis can be started immediately by running the following commands from the directory *demo/*.

The most recent version 9.0 of the EUCAST Breakpoint Tables, which is valid from 1.1.2019, has already been pre-processed for convenience and is included in the package under *demo/demo_resources/preprocessed_v_9.0_Breakpoint_Tables.xlsx*.

Other versions can also be downloaded and used. Please see :ref:`preprocessing`.

The pre-processed EUCAST Breakpoint Tables can be parsed into a dataframe of organism-compound breakpoints using the following command :ref:`EucastParser.run_eucast_parser()<EucastParser.run_eucast_parser>`.

**Preparation for Parsing:**
::
   from pymicruler.bp.EucastParser import EucastParser
   import os

   path_to_preprocessed_infile = os.path.join('demo_resources', 'preprocessed_v_9.0_Breakpoint_Tables.xlsx')

   path_to_parser_outfile = os.path.join('demo_results', 'processed_v_9.0_Breakpoint_Tables.xlsx')


**Parsing:**
::
   # instantiate EUCAST parser object
   ep = EucastParser()

   # parse preprocessed EUCAST table; returns Pandas DataFrame
   eucast_9_0 = ep.run_eucast_parser(path_to_preprocessed_infile)

   # write PandasDataFrame to Excel
   if not os.path.exists('demo_results'):
       os.makedirs('demo_results')

   eucast_9_0.to_excel(path_to_parser_outfile, index=False)

**Parsed EUCAST Breakpoint Table:**

.. list-table::
   :header-rows: 1

   * - organism
     - cmp_name
     - s_value
     - r_value
     - exception
     - high_exposure
     - exception
     - roa
     - indication
     - source
   * - Enterobacterales
     - Benzylpenicillin
     - -1
     - 0
     -
     -
     -
     -
     -
     - bp
   * - Enterobacterales
     - Ampicillin
     - 8
     - 8
     -
     -
     -
     -
     -
     - bp
   * - Enterobacterales
     - Ampicillin-sulbactam
     - 8
     - 8
     -
     -
     -
     -
     -
     - bp
   * - Enterobacterales
     - Amoxicillin
     - 8
     - 8
     -
     -
     -
     -
     -
     - bp

**Preparation for MIC Analysis**
::
   from pymicruler.bp.BpRuler import BpRuler
   import pandas as pd

   path_to_mics = os.path.join('demp_resources', 'mic_demo_table.xlsx')
   mics_df = pd.read_excel(path_to_mics)


**Breakpoint Query**

Breakpoints for organism-compound combinations can subsequently be looked up using the following method :ref:`BpRuler.run_breakpoint_query()<BpRuler.run_breakpoint_query>`.
This method takes the lineage of the target organisms in account.
::
   bp = BpRuler()
   bp_table = bp.run_breakpoint_query(path_to_parser_outfile, mics_df)
   print(bp_table.head(10))

**Results of Breakpoint Query:**

.. list-table::
   :header-rows: 1

   * - sample_id
     - organism
     - cmp_name
     - MIC
     - s_value
     - r_value
     - matched_organism
     - matched_cmp_name
   * - 4710
     - Stenotrophomonas maltophilia
     - Ampicillin-sulbactam
     - 128
     - -1
     - 0
     - Stenotrophomonas maltophilia
     - Ampicillin-sulbactam
   * - 4710
     - Stenotrophomonas maltophilia
     - Ampicillin
     - 256
     - -1
     - 0
     - Stenotrophomonas maltophilia
     - Ampicillin
   * - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
   * - 4710
     - Stenotrophomonas maltophilia
     - Levofloxacin
     - 4
     -
     -
     - Breakpoint not found
     -
   * - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
   * - 4710
     - Stenotrophomonas maltophilia
     - Trimethoprim-sulfamethoxazole
     - 0.25
     - 4
     - 4
     - Stenotrophomonas maltophilia
     - Trimethoprim-sulfamethoxazole


**MIC Classificaion**

Individual AST results can be classified into phenotypes (R, S, I) via the following command :ref:`BpRuler.run_sample_classification()<BpRuler.run_sample_classification>`:
::
   bp = BpRuler()
   label_table = bp.run_sample_classification(path_to_parser_outfile, mics_df)
   print(label_table.head(10))


**Results of MIC Classification:**

.. list-table::
   :header-rows: 1

   * - sample_id
     - organism
     - cmp_name
     - MIC
     - s_value
     - r_value
     - matched_organism
     - matched_cmp_name
     - label
   * - 4710
     - Stenotrophomonas maltophilia
     - Ampicillin-sulbactam
     - 128
     - -1
     - 0
     - Stenotrophomonas maltophilia
     - Ampicillin-sulbactam
     - R
   * - 4710
     - Stenotrophomonas maltophilia
     - Ampicillin
     - 256
     - -1
     - 0
     - Stenotrophomonas maltophilia
     - Ampicillin
     - R
   * - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
   * - 4710
     - Stenotrophomonas maltophilia
     - Levofloxacin
     - 4
     -
     -
     - Breakpoint not found
     -
     -
   * - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
   * - 4710
     - Stenotrophomonas maltophilia
     - Trimethoprim-sulfamethoxazole
     - 0.25
     - 4
     - 4
     - Stenotrophomonas maltophilia
     - Trimethoprim-sulfamethoxazole
     - S


**Whole resistance phenotype determination**

EUCAST's interpretive rules - that additionally infer phenotypes for compounds that were not tested - can be applied for the classification of phenotypes from AST data by the following method :ref:`BpRuler.get_whole_resistance_phenotype()<BpRuler.get_whole_resistance_phenotype>`:
::
   bp = BpRuler()
   full_table = bp.get_whole_resistance_phenotype(path_to_parser_outfile, mics_df)
   print(full_table.head(10))

**Results of whole resistance phenotype determination:**

.. list-table::
   :header-rows: 1

   * - sample_id
     - organism
     - cmp_name
     - MIC
     - s_value
     - r_value
     - matched_organism
     - matched_cmp_name
     - label
   * - 4710
     - Stenotrophomonas maltophilia
     - Ampicillin-sulbactam
     - 128
     - -1
     - 0
     - Stenotrophomonas maltophilia
     - Ampicillin-sulbactam
     - R
   * - 4710
     - Stenotrophomonas maltophilia
     - Ampicillin
     - 256
     - -1
     - 0
     - Stenotrophomonas maltophilia
     - Ampicillin
     - R
   * - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
   * - 4710
     - Stenotrophomonas maltophilia
     - Levofloxacin
     - 4
     -
     -
     - Breakpoint not found
     -
     -
   * - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
   * - 4710
     - Stenotrophomonas maltophilia
     - Trimethoprim-sulfamethoxazole
     - 0.25
     - 4
     - 4
     - Stenotrophomonas maltophilia
     - Trimethoprim-sulfamethoxazole
     - S

For the convenience of the user a couple of demo scripts which allow to get an overview of the described functionalities are provided in the folder *demo/*.