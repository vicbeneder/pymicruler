Limitations
===========
    - Backward compatibility:
        Only breakpoint tables version 7.1 and more recent have been parsed and tested.

    - Pre-processing:
        Currently, the automatic pre-processing via the function is very sensitive to any changes.
        Generally the macro should be deleted from the Excel file again after every run to ensure correct execution.

        Strikethrough text cannot be differentiated from normal text by the parser and will therefore be transcribed with the rest of the
        text if it is not removed manually.

    - Route of Administration and Indication:
        Information on the route of administration and particular indications can not be considered in the query directly.
        This information is, however, saved in the parsed Breakpoint table and can be accessed manually if needed.

        During the processing some breakpoints are filtered if more than one route of administration or indication were provided.
        In these cases breakpoints that were applicable to no specific indication and breakpoints aiming at intravenous administration were preferred.

    - Intrinsic resistances:
        While the breakpoint table can be updated easily by parsing it again via the provided functions in this package,
        the intrinsic resistance table was developed manually as the information is provided in a pdf file only.
        In case of a new publication follow the steps outlined in the :ref:`manual updates section<intrinsic_resistances>`.

    - Interpretive rules:
        + Manual Curation:
            The rules of the rule based engine were transcribed manually based on the
            Expert Rules and Intrinsic Resistances version 2.0 document. If newer versions are published they have to be updated according to the steps outlined in the :ref:`manual updates section<interpretive_rules>`.

        + Inclusion of additional information:
            Some of the rules rely on additional information regarding the sample, such as whether Beta-Lactamase is present.
            At this moment there is no sensible way to consider this information in the mic label detemination workflow.
