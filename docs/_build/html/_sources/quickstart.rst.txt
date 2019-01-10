Quickstart
==========

After :ref:`installation` of the package the analysis can be started by executing the demo scripts included in the package.

The most recent version 9.0 of the Eucast Breakpoints Table which is valid from 1.1.2019 has been pre-processed and is stored in /demo/demo_resources/preprocessed_v_9.0_Breakpoint_Tables.xlsx.

If any other versions should be used, download the respective file and follow the steps for :ref:`preprocessing`.

To parse the preprocessed Clinical Breakpoint Table execute the method :ref:`EucastParser.run_eucast_parser()<EucastParser.run_eucast_parser>`:
::
    from pymicruler.bp.EucastParser import EucastParser
    from pymicruler.utils import util

    ep = EucastParser()
    eucast = ep.run_eucast_parser(path_to_preprocessed_infile)

    eucast.to_excel(path_to_guidelines, index=False)


Breakpoints can be looked up by executing the method :ref:`BpRuler.run_breakpoint_query()<BpRuler.run_breakpoint_query>`:
::
    from pymicruler.bp.BpRuler import BpRuler

    bp = BpRuler()
    bp_table = bp.run_breakpoint_query(path_to_guidelines, test_bp_data_small)


AST results can be translated into resistance phenotypes (R, S, I) by executing the method :ref:`BpRuler.run_sample_classification()<BpRuler.run_sample_classification>`:
::
    from pymicruler.bp.BpRuler import BpRuler

    bp = BpRuler()
    label_table = bp.run_sample_classification(path_to_resource, test_bp_data_small)


Resistance phenotypes for tested components and beyond can be derived from AST data by executing the method :ref:`BpRuler.get_whole_resistance_phenotype()<BpRuler.get_whole_resistance_phenotype>`:
::
    from pymicruler.bp.BpRuler import BpRuler

    bp = BpRuler()
    full_table = bp.get_whole_resistance_phenotype(path_to_resource, test_bp_data_small)


