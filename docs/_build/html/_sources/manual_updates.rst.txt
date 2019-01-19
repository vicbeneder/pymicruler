Manual Updates
===============

.. _clinical_breakpoint_tables:

Updated Clinical Breakpoint Tables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the overall table structure of the updated Clinical Breakpoint Tables
remains the same, the file may be parsed as described in the section :ref:`quickstart`.
The most probable changes are the addition of new notes, new entries and
changes in the interpretive rules:

New notes
-------------
The most frequent differences between versions of the Clinical Breakpoint Tables
are changes in the wording of the notes which provide further information to
specific breakpoints.

All notes which have been published within EUCAST Clinical Breakpoint Tables 7.1 to 9.0 have been saved and analysed
manually and will be interpreted automatically by the parser.
In case of any new or altered notes the user is asked to update this classification
either in a guided way directly via the :ref:`console<console_class>` or by saving all new comments in the Excel file *pymicruler/output/missing_notes.xlsx* for subsequent :ref:`manual incorporation<manual_inc>`.

.. _console_class:

**A. Console Classification**

In case the user decides to classify the new notes via the console, he will be asked to answer a set of questions about the content of the note.

**1) Relevance**

Initially notes which are irrelevant for the AST interpretation, e.g. information about how to perform the AST itself, should be filtered out via the following question:

*'May this information relevant for further breakpoint classification? (y/n)'*

No (*'n'*) should be chosen only if no information for the interpretation of AST result is given, i.e.

*'Agar dilution is the reference method for fosfomycin. MICs must be determined in the presence of glucose-6-phosphate (25 mg/L in the medium). Follow the manufacturers' instructions for commercial systems.'*


In any other cases, also in case of uncertainty, it is best to classify the information as relevant by choosing (*'y'*)
An example for a relevant comment would be:

*'Tetracycline has been used to predict doxycycline susceptibility for
the treatment of Yersinia enterocolitica infections (tetracycline MIC ≤4
mg/L for wild-type isolates).'*


**2) Content**

If the comment is found to be relevant the next question aims at
determining the content of the note. For this purpose the user has to
classify the note into one of six types of information or a 'back-up' option if it
does not match any of the other options.

| *'Does this comment*
| *(a) contain any information about how to derive the resistance phenotype from            other resistances or susceptibilities (interpretive rules)?*
| *(b) explicitly say that the species can be considered resistant?*
| *(c) contain any information about the route of administration?*
| *(d) contain any information about the indication the agent should be used for?*
| *(e) contain any information about a species that is excepted from the general rule?*
| *(f) contain a complete breakpoint including information about species, compound and MIC?*
| *(g) not add any information that can be directly encoded in the table?'*

**3) Further information about choices**

**a. Interpretive rules**
  An interpretive rule provides information on how to derive resistance phenotypes across antimicrobial agents via a shared mechanism of action. One example would be:

  *'For isolates susceptible to benzylpenicillin, susceptibility can be inferred from benzylpenicillin or ampicillin. '*

  All new rules will have to be added to the rule as described in Section :ref:`Changes in the interpretive rules<int_rules_table>`

**b. Resistance**
  Should be chosen if the comment specifically mentions that the organism is resistant to the agent, e.g.

  *'Enterococci are intrinsically resistant to aminoglycosides and aminoglycoside monotherapy is ineffective.'*


**c. Route of administration**
  Should be chosen if any route of admnistration is mentioned in the comment text, e.g.

  *'The breakpoints are based on epidemiological cut-off values (ECOFFs) and apply to oral treatment of C. difficile infections with vancomycin.'*

  In a further question the user is then asked to specify the mentioned route of administration.

  Options are:
     - iv (=intravenous)
     - oral
     - topical
     - nasal

**d. Indication**
  Should be chosen if information about the disease that should be treated is given, e.g.

  *'Breakpoints relate to meningitis only.' or 'Breakpoints for penicillins other than benzylpenicillin relate only to non-meningitis isolates.'*

  In a further question the user is asked to specify the mentioned indication.
  In the first example the answer would be 'meningitis' as the breakpoint is only applicable to this indication.

  If the breakpoint is excepted for a specific indication as in the second example, 'NOT meningitis' would be the answer.


**e. Exception**
  Should be chosen if any species or genus is explicitly excluded from the applicability of the guideline, e.g.

  *'Breakpoints do not apply to Plesiomonas shigelloides since aminoglycosides have low intrinsic activity against this species.'*

  In the follow up question the mentioned species should, if possible, be specified with its full name, i.e. *'Escherichia coli'* instead of *'E. coli'*


**f. Breakpoint**
  Should be chosen if the comment contains a whole breakpoint specifying organism, compound and S- and R- concentrations.

  *'Azithromycin has been used in the treatment of infections with Salmonella Typhi (MIC ≤16 mg/L for wild type isolates) and Shigella spp.'*

  In the follow up question the breakpoint should then be specified as follows:

  *'Salmonella enterica subsp. enterica serovar Typhi; Azithromycin; 16'*


**g. Not encodable**
  Should be chosen if none of the other options did match. In this case the information is relevant for the interpretation but it currently cannot be included in the analysis.
  Future developments of the package may include displaying this additional information when a breakpoint is looked up.

.. _manual_inc:

**B. Altering the interpretation dictionary manually**

If there are more than a hand full of comments and the classification system is clear to the user, editing the responsible dictionary directly might be more efficient.
New notes will be saved in the file *pymicruler/output/missing_notes.xlsx*.

The note text has to be copied into the 'interpretation_dict_updated.xlsx' file in the same folder:

.. list-table:: Interpretation Dictionary
   :header-rows: 1

   * - note_text
     - relevance
     - interpretation
     - rule
     - exception
     - indication
     - new_bp
     - not_encodable
     - resistance
     - roa
     - other_information
   * - Agar dilution is the reference method for mecillinam MIC determination.
     - 0
     -
     -
     -
     -
     -
     -
     -
     -
     -
   * - Always test for beta-lactamase. If positive, report resistant to benzylpenicillin, ampicillin and amoxicillin. Tests based on a chromogenic cephalosporin can be used to detect the beta-lactamase. The susceptibility of beta-lactamase negative isolates to ampicillin and amoxicillin can be inferred from benzylpenicillin.
     - 1
     - 1
     - rule_10_4; n_gonorrhoeae_penicillin_1
     -
     -
     -
     -
     -
     -
     -
   * - Azithromycin has been used in the treatment of infections with Salmonella Typhi (MIC ≤16 mg/L for wild type isolates) and Shigella spp.
     - 1
     -
     -
     - Shigella
     -
     - Salmonella enterica subsp. enterica serovar Typhi; Azithromycin; 16
     -
     -
     -
     -
   * - Breakpoints for penicillins other than benzylpenicillin relate only to non meningitis isolates.
     - 1
     -
     -
     -
     - NOT meningitis
     -
     -
     -
     -
     -


Based on this note text the following columns have to be filled:

         :relevance: has to be filled with '1' if the comment is found to be relevant for AST results interpretation, otherwise with '0'. In the latter case all other columns should stay empty.

         :interpretation: Does this comment contain an interpretive rule (Yes: '1', No: '').

         :rule: After implementation of the interpretation rule in the rule based engine, insert the name of the function representing the rule.

         :exception: Put name of any organisms that are excepted from the general rule. Full name is preferred, e.g. 'Escherichia coli' instead of 'E. coli'

         :indication: Put any disease that is excepted from the rule or the only one that the rule applies to , e.g. 'NOT meningitis' or 'meningitis'

         :new_bp: If a whole breakpoint is mentioned in the comment enter it in the following format: species; agent; S; R.

         :not_encodable: Other information that cannot be put in any of the other categories.

         :resistance: '1' if the breakpoint explicitly mentions that the bacterium is resistant to the agent.

         :roa: Put the route of administration ('iv', 'oral', 'nasal', 'topical') if mentioned.




New entries
-------------

**A. Organisms**

To correctly connect rules along the taxonomic lineage, organisms need to be mapped against the
NCBI Taxonomy. Already during the parsing process a quality check is performed to ensure all
organisms mentioned in the guidelines can be mapped. If any of the entries does not pass this
test, the parser will print the following message:

*The following organisms could not be matched against the NCBI Taxonomy: <names>.*

There are different reasons why organisms cannot be mapped:

   **1. Phenotypically defined groups**

      Many antibiotics work only on bacteria which show a specific phenotype, e.g. gram-negative bacteria or coagulase-negative staphylococci. As these groups are not defined by the NCBI Taxonomy they are resolved into their member species.

      For new phenotypically defined groups to be interpreted correctly they have to be added to the file *pymicruler/resources/phenotypic_groups.xlsx*.

      Each group is defined on a separate sheet. The header of the first column is the name of the phenotypically defined group as written in the EUCAST Breakpoint Tables and the organisms that show the phenotype are appended to the column.


.. _reclass:

   **2. Organism has been reclassified**

      Especially if older versions of the EUCAST Breakpoint Tables are parsed it is possible that organisms have been reclassified and can thus not be mapped via the name mentioned in the table.

      These outdated name can be added to the file *pymicruler/resources/species_renaming.xlsx* containing a list of terms which are automatically translated during the processing.

      The entry that cannot be matched should be pasted in the first column *'query_term'* and the full names as listed in the current version of the NCBI Taxonomy should be added in the second column *'replacement'*

      **Species Renaming Document**

      .. list-table::
         :header-rows: 1

         * - query_term
           - replacement
         * - P. mirabilis
           - Proteus mirabilis
         * - Clostridium difficile
           - Clostridioides difficile
         * - Enterobacter aerogenes
           - Klebsiella aerogenes

   **3. Short forms are used**

      Finally, abbreviations of species names, i.e. *E. coli* are commonly used in comments, exceptions and restrictions but cannot be mapped to the NCBI Taxonomy either. They are, however, detected separately and lead to the following error message:

      *A new organism name was found which could not be translated: <name>.*

      To ensure proper interpretation the user is asked to add any new abbreviations to the document *species_renaming.xlsx* as described in Section :ref:`2. Organism has been reclassified<reclass>` above.

**B. Compounds**

Similar to the taxonomy in case of the organism, although certainly less sophisticated, compounds are grouped into compound classes, i.e. penicillins or aminoglycosides and sub-classes such as the aminopenicillins.

In case the parser cannot derive information about the compound class of an antimicrobial compound automatically, e.g. if EUCAST published breakpoints for a new compound, it will display the following error message:

*The following compounds were not found in the compound dictionary: <names>*

The user is asked to add any new compounds to the respective compound class in the file *pymicruler/resources/compound_classes.xlsx*. The information which class the compound belongs to can be derived from the EUCAST Table itself.


**C. Other information**

If there are any keywords written within the breakpoint entry, e.g. information in parentheses which do not match any of the known information the following message will be displayed:

**A new type of information was found which could not be categorised <information>.**

Based on previous publication these keywords refer to one of three types of information:

**1. Indication**
  If the information which could not be categorizes is a disease, the user is asked to manually append this information to the script to the class *Info*, list *IND* in the file utils/util.py.

**2. Irrelevant information for AST**
  If the information is not relevant for further AST result interpretation, the user is asked to manually add this information to the class *Info*, list *IRR_PARR* in the file utils/util.py.

**3. Organism**

  If the information about a restriction to a specific organism the user is asked to adapt the pattern called *PAR*, listed in the script *utils/util.py* in the class *CmpRegex*.

  Currently all parenthesis entries starting with *'except'* restrictions to specific organisms which are dealt with in subsequent steps of the analysis. This pattern needs to be extended to match also other cases of information about organisms.



.. _int_rules_table:

Changes in the interpretive rules
-------------------------------------

While a big share of the interpretive rules are published in an separate document, some of the rules
are only mentioned within the note text of the EUCAST Clinical Breakpoint Tables. As these notes
may change with every new publication and rules need to be translated manually, the user may have to adapt the rule based engine encoded in
*pymicruler/bp/RuleBasedEngine.py* in case of a new publication.

**A. Tracking changes**

During the manual classification of new notes the user also defines whether notes do contain any interpretive rules. The library will then treat these notes differently throughout the analysis, tracking all breakpoints they are applicable to. Eventually it is assessed whether the occurrence of these interpretive rules have changed from the last version. After the analysis is completed this log of all changes is saved in *pymicruler/output/interpretive_rule_changes.csv*. It can be expected to look as follows:

.. list-table::
         :widths: 15 10 30
         :header-rows: 1

         * - Note_text
           - associated_to
           - type_of_change
         * - The aztreonam breakpoints for Enterobacteriaceae will detect clinically important resistance mechanisms (including ESBL).
           - ('Enterobacterales', 'Aztreonam')
           - removed all
         * - Susceptibility of staphylococci to cephalosporins is inferred from the cefoxitin susceptibility except for cefixime, ceftazidime, ceftazidime-avibactam, ceftibuten and ceftolozane-tazobactam, which do not have breakpoints and should not be used for staphylococcal infections.
           - ('Staphylococcus spp.', 'Cefaclor'), ('Staphylococcus spp.', 'Cefadroxil')
           - removed all
         * - Isolates susceptible to linezolid can be reported susceptible to tedizolid.
           - ('Staphylococcus spp.', 'Tedizolid')
           - added
         * - Erythromycin can be used to determine susceptibility to azithromycin, clarithromycin and roxithromycin.
           - ('Staphylococcus spp.', 'Azithromycin'), ('Staphylococcus spp.', 'Clarithromycin')
           - added all


In the first column of the document the texts of the notes with changed occurrences are listed. The second column describes the breakpoints that have been affected and the third column how they changed, i.e. *'added'* or *'removed'*.

In this context **'added'** indicates that the application of the interpretive rules needs to be extended for the mentioned species/compound combinations and
**'removed'** means that these breakpoints have to be excepted from the application of the rule.
If the keyword 'all' is appended as in *'added_all'* and *'removed_all'* the rule has to be established or can be removed as a whole.

These changes then have to be implemented in the rule based engine in the script *pymicruler/bp/RuleBasedEngine.py* manually. Names of the rules that need to be changed can be looked up in the corresponding entry for the note in the document *pymicruler/output/interpretation_dict_updated.xlsx*. The information is stored in the in the column *'rule'*.

.. _pyknow_rules:

**B. Pyknow Rules**

To better understand how these rules need to be edited, the parts of such *pyknow* rules which make up the rule based engine will be explained shortly. For more detailed information regarding the syntax and function of *pyknow* rules, please consult the `documentation of the package <https://pyknow.readthedocs.io/en/stable/>`_.

One example for a EUCAST note describing an interpretive rule is:

*Ampicillin susceptible S. saprophyticus are mecA-negative and susceptible to ampicillin, amoxicillin and piperacillin (without or with a beta-lactamase inhibitor).*

Translated to a *pyknow* rule it would look as follows:
::
   @Rule(AND(Organism(name='Staphylococcus saprophyticus'),
              Susceptibility(cmp_name='Ampicillin')))
    def exec_rule_bp_t_staphylococcus_penicillins_3(self):
        cmp_list = ('Ampicillin', 'Amoxicillin', 'Amoxycillin-clavulanic acid',
                    'Ampicillin-sulbactam', 'Piperacillin', 'Piperacillin-tazobactam')
        self.declare(Mec(present='False'))
        self.declare_cmp_list(cmp_list, 'S')

Rules generally consist of a pattern matching part and an executing part. In this case the pattern matching part is:
::
   @Rule(AND(Organism(name='Staphylococcus saprophyticus'),
              Susceptibility(cmp_name='Ampicillin')))

If the analysed organism is *Staphylococcus saprophyticus* and it is classified as susceptible to Ampicillin based on the AST results the
corresponding function is executed:
::
   def exec_rule_bp_t_staphylococcus_penicillins_3(self):
        cmp_list = ('Ampicillin', 'Amoxicillin', 'Amoxycillin-clavulanic acid',
                    'Ampicillin-sulbactam', 'Piperacillin', 'Piperacillin-tazobactam')
        self.declare(Mec(present='False'))
        self.declare_cmp_list(cmp_list, 'S')

The function then adds the derived phenotypes (susceptible to Ampicillin-sulbactam, Amoxicillin,
Amoxycillin-clavulanic acid, Piperacillin and Piperacillin-tazobactam) to the set of known
resistance phenotypes of the sample.


**C. Adapting rules**

**1. Adapt matching condition**

If the applicability for the rule should be changed (e.g. extend to Staphylococcus aureus) the matching condition has to be altered to:
::
   @Rule(AND(Organism(name=anyof('Staphylococcus saprophyticus', 'Staphylococcus aureus'),
              Susceptibility(cmp_name='Ampicillin')))

If more than one susceptibility have to be present e.g. susceptible to Ampicillin and to Amoxicillin, the matching condition would be updated as follows:
::
   @Rule(AND(Organism(name=anyof('Staphylococcus saprophyticus', 'Staphylococcus aureus'),
              AND(Susceptibility(cmp_name='Ampicillin'),
              Susceptibility(cmp_name='Amoxicillin'))

**2. Adapt executing function**

In the executing part of the function all phenotypes that can be derived should be declared.
This can be done for each compound individually:
::
   self.declare(Resistance(cmp_name='Benzylpenicillin'))
   self.declare(Susceptibility(cmp_name='Ciprofloxacin'))
   self.declare(Intermediate(cmp_name='Tetracycline'))

For a whole compound family, e.g. resistance to all aminoglycosides:
::
   self.declare_cmp_family('Aminoglycosides', 'R')

Or, for a list of compounds if all compounds have to be declared for the same phenotype, e.g. susceptible:
::
   cmp_list = ['Benzylpenicillin', 'Ciprofloxacin', 'Tetracycline']
   self.declare_cmp_list(cmp_list, 'S)


**3. Creating new rules**

If completely new interpretive rule are found, new *pyknow* rule have to be developed by taking the example described in the :ref:`last section<pyknow_rules>` as a reference.
The order of the rules does not change the result of he analysis so rules can simply be appended to the class *BacterialResistance* of the script *pymicruler/bp/RuleBasedEngine.py*.

The name of the function that is executed can be changed deliberately as it will only be called
after matching the corresponding rule. To ensure traceability of the source of the information
the suggested naming scheme is the following:

All functions start with the term '`exec_rule_`' then the EUCAST document is specified.
If the rule is derived from the breakpoint table the abbreviation is '`bp_t_`'.
Then, for the example mentioned above, the sheet `staphylococcus` and compound family '`penicillins`' are added and finally the number of the comment '`3`' is appended.


Changes in the table layout
----------------------------
If the content of the column remains the same but only their position within the table changes the
user is asked to update the new column indices(starting with 0) for the block headers 'MIC', 'R >' and 'S <=' the file *utils/util.py*.


Changes in the headlines
------------------------
As different sheets have slightly varying column structures even within one publication, some headlines are used as anchors for the processing of a new unit of information.
If headlines have been renamed, the corresponding regular expression patterns have to be updated in the class *Regex* in the file *utils/util.py*


.. _intrinsic_resistances:

Updated Intrinsic Resistances Publication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Currently all information about intrinsic resistances is stored in the file *resources/final_ires.csv*, which is based on version 3.1 of the EUCAST intrinsic resistance document.
As this table was transcribed manually, the user is asked to incorporate any changes in the table directly.

.. list-table::
         :header-rows: 1

         * - organism
           - cmp_name
           - s_value
           - r_value
           - exception
           - roa
           - indication
           - identifier
         * - Burkholderia cepacia complex
           - Amikacin
           - -1
           - 0
           -
           -
           -
           - 2_3
         * - Stenotrophomonas maltophilia
           - Amikacin
           - -1
           - 0
           -
           -
           -
           - 2_7
         * - Streptococcus
           - Amikacin
           - -1
           - 0
           -
           -
           -
           - 4_6
         * - Enterococcus faecalis
           - Amikacin
           - -1
           - 0
           -
           -
           -
           - 4_7

The name of the pathogen and compound have to be added to the columns *'organism'* and
*'cmp_name'* respectively and the S- and R- concentrations are per default -1 and 0.
The information in the column column 'indicator' maps the information back to the original numbering in the publication.
Ideally it should be updated whenever the document is updated.


.. _interpretive_rules:

Updated Interpretive Rules Publication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In case of an update in the Interpretive Rule publication the user is asked to edit the rule based engine manually.
The current naming scheme allows to connect the rule back to their listing in v3.1 of the Expert Rules and Intrinsic Resistances.
It might be best to compare the new rules to the then outdated publication to find the changed rule in the most efficient way.
For further information on how to adapt old rules or create new rules, see :ref:`Changes in interpretive rules<int_rules_table>`.