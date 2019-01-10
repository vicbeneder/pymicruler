Modules
=======

The package allows the user to execute the following methods:

EucastParser
^^^^^^^^^^^^
.. _EucastParser.run_eucast_parser:
- Parse Eucast Clinical Breakpoint Table
    + EucastParser.run_eucast_parser(path)
        Arguments:
            'path': Path to preprocessed Eucast Clinical Breakpoint Table
        Returns:
            Pandas DataFrame of parsed guidelines


BpRuler
^^^^^^^^
.. _BpRuler.run_breakpoint_query:
- Search breakpoints based on organism and compound combinations:
   + BpRuler.run_breakpoint_query(path_to_resource, query_df)
      Arguments:
         'path_to_resource': Path to parsed Clinical Breakpoint Table
         'query_df': Pandas DataFrame containing organism-compound combinations to look up. Has to contain column names 'organism' and 'cmp_name'.
      Returns:
         Pandas DataFrame of parsed guidelines containing the following additional columns:
            - 'matched_organism': The species/genus/family the breakpoint is applicable to
            - 'matched_cmp_name': The compound name the breakpoint is applicable to
            - 's_value': The lower border of the breakpoint in mg/L.
            - 'r_value': The upper border of the breakpoint in mg/L.

.. _BpRuler.run_sample_classification:
- Derive resistance phenotypes from Minimum inhibitory concentrations (MIC).
    + BpRuler.run_sample_classification(resource, query_df)
        Arguments:
            'path_to_resource': Path to parsed Clinical Breakpoint Table
            'query_df': Pandas DataFrame containing organism-compound combinations to look up.
            Has to contain column names 'organism', 'cmp_name' and 'MIC'.

            If a column 'sample_id' is added interpretive rules are applied to the provided sample information to find information about any organism-compound information for which no breakpoint was found.
        Returns:
            Pandas DataFrame of parsed guidelines containing the following additional columns:
               - 'matched_organism': The species/genus/family the breakpoint is applicable to
               - 'matched_cmp_name': The compound name the breakpoint is applicable to
               - 's_value': The lower border of the breakpoint in mg/L.
               - 'r_value': The upper border of the breakpoint in mg/L.
               - 'label': The resistance phenotype 'R', 'S', or 'I' derived from the breakpoint and MIC.


.. _BpRuler.get_whole_resistance_phenotype:
- Derive resistance phenotypes based on AST results and beyond that via interpretive rule.
    + BpRuler.get_whole_resistance_phenotype(resource, query_df)
        Arguments:
            'path_to_resource': Path to parsed Clinical Breakpoint Table
            'query_df': Pandas DataFrame containing organism-compound combinations to look up.
            Has to contain column names 'organism', 'cmp_name', 'MIC' and 'sample_id'.
        Returns:
            Pandas DataFrame of parsed guidelines containing the following additional columns:
               - 'matched_organism': The species/genus/family the breakpoint is applicable to
               - 'matched_cmp_name': The compound name the breakpoint is applicable to
               - 's_value': The lower border of the breakpoint in mg/L.
               - 'r_value': The upper border of the breakpoint in mg/L.
               - 'label': The resistance phenotype 'R', 'S', or 'I' derived from the breakpoint and MIC.

