Quickstart
==========

After :ref:`installation` of the package the analysis can be started by executing the demo scripts included in the package.

The most recent version 9.0 of the Eucast Breakpoints Table which is valid from 1.1.2019 has been pre-processed and is stored in /demo/demo_resources/preprocessed_v_9.0_Breakpoint_Tables.xlsx.

If any other versions should be used, download the respective file and follow the steps for :ref:`preprocessing`.

To parse the preprocessed Clinical Breakpoint Table execute the method :ref:`EucastParser.run_eucast_parser()<EucastParser.run_eucast_parser>`:
::
    from pymicruler.bp.EucastParser import EucastParser

    ep = EucastParser()
    eucast = ep.run_eucast_parser(path_to_preprocessed_infile)

    eucast.to_excel(path_to_guidelines, index=False)

.. list-table:: Parsed EUCAST Breakpoint Table
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



Breakpoints can be looked up by executing the method :ref:`BpRuler.run_breakpoint_query()<BpRuler.run_breakpoint_query>`:
::
    from pymicruler.bp.BpRuler import BpRuler

    bp = BpRuler()
    bp_table = bp.run_breakpoint_query(path_to_guidelines, test_bp_data_small)
    print(bp_table.head())

.. list-table:: Results of Breakpoint Query
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

AST results can be translated into resistance phenotypes (R, S, I) by executing the method :ref:`BpRuler.run_sample_classification()<BpRuler.run_sample_classification>`:
::
    from pymicruler.bp.BpRuler import BpRuler

    bp = BpRuler()
    label_table = bp.run_sample_classification(path_to_resource, test_bp_data_small)
    print(label_table.head())

.. list-table:: Results of MIC classification
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


Resistance phenotypes for tested components and beyond can be derived from AST data by executing the method :ref:`BpRuler.get_whole_resistance_phenotype()<BpRuler.get_whole_resistance_phenotype>`:
::
    from pymicruler.bp.BpRuler import BpRuler

    bp = BpRuler()
    full_table = bp.get_whole_resistance_phenotype(path_to_resource, test_bp_data_small)
    print(full_table.head())

.. list-table:: Results of whole resistance phenotype determination
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

