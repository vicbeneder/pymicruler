Data processing
================

Alternative breakpoint information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Some breakpoints do not contain concentrations to classify test result as there is too little evidence that therapy will be successful.
Following the interpretation EUCAST provides in the table directly we converted and filtered these entries as follows:
    '-': a dash means that susceptibility testing is not recommended and that the species can be considered resistant.
         The respective concentrations are then changed to S <= -1 and R > 0
         mg/L unless any notes associated to the rule contain contradictory
         information
    'IP': 'in preparation'. These entries are currently dropped due to uncertainty regarding
         the classification.
    'IE': 'insufficient evidence' that the organism or group is a good target for therapy with the agent'.
        These entries are currently dropped due to uncertainty regarding the classification.
    'NA': 'not applicable'. Used for screen breakpoints to differentiate between isolates with and without resistance mechanism.
        These entries are dropped.

Phenotypically defined groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To map all organisms mentioned in the publications back to the NCBI taxonomy we had to resolve phenotypically defined groups into the the individual species that show this phenotype.
    Groups that were defined within the Eucast Breakpoint table:
        - Viridans group streptococci,
        - Gram-positive anaerobes
        - Gram-negative anaerobes
        - Non-fermentative gram-negative

    Groups whose member species had to be looked up:
        - Streptococcus groups A, B, C and G
        - Gram negative bacteria
        - Gram positive bacteria

All phenotypically defined group members can be updated by changing the Excel stored in pymicruler/resources/phenotypic_groups.xlsx.


Preference of general breakpoint over specific entry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Additional information such as route of administration or indication may currently not be included in the query.
We therefore filtered out more specific breakpoints (e.g. only in case of treatment against meningitis) in cases where also a more general breakpoint was provided.

If breakpoints for both oral and intravenous administration of the drug were published, the breakpoint for intravenous administration was preferred.
