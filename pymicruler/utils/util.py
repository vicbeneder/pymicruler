from enum import Enum
import pandas as pd

from pymicruler.bp import config_resource, config_output


# Contains essential columns for different steps throughout the analysis
class Cols(Enum):
    PARS_OUT = ['organism', 'cmp_name', 's_value', 'r_value', 'exception',
                'high_exposure', 'roa', 'indication',  'source']
    PROC = ['organism', 'cmp_name', 'cmp_family', 's_value', 'r_value',
            's_ss', 'r_ss', 'all_ss', 'compound_ss', 'exception', 'roa',
            'indication', 'high_exposure']
    BODY = ['cmp_name', 'parenthesis', 'roa', 'cmp_ss', 'restrictions',
            'high_exposure']
    IRU = ['Note_text', 'associated_to', 'type_of_change']
    BP = ['organism', 'cmp_name']
    CLASS = ['organism', 'cmp_name', 'MIC']
    FULL = ['organism', 'cmp_name', 'MIC', 'sample_id']
    RED = ['organism', 'cmp_name', 'cmp_family', 's_value', 'r_value',
           'exception', 'high_exposure', 'roa', 'indication']
    BP_OUT = ['cmp_name', 's_value', 'r_value', 'notes']
    RULER_DROP_ELSE = ['lineage', 'organism_id']
    ADDED_SMPL = ['s_value', 'r_value', 'matched_organism', 'matched_cmp_name', 'label']
    ADDED_BP = ['s_value', 'r_value', 'matched_organism', 'matched_cmp_name']


# Paths to external resources for analysis
class Path(Enum):
    IDICT = config_output('interpretation_dict_updated')
    MISSING_NOTES = config_output('missing_notes')
    OLD_OCC = config_resource('interpretive_text')
    IRU_CHANGES = config_output('interpretive_rule_changes')
    RENAME = config_resource('species_renaming')
    IRES = config_resource('ires')
    C_CLASS = config_resource('compound_classes')
    PHEN_G = config_resource('phen_groups')


# Contains column indices for main columns in the Eucast Breakpoint Tables
class ColPosStd(Enum):
    CMP_NAME = 0
    S = 1
    MIC = 1
    R = 2


# Patterns for regular expressions used throughout the analysis
class Regex(Enum):
    # Matches the MIC headline (as indicator of a new block) for versions 7.1 - 9.0
    MIC = 'MIC breakpoints?\s*\(mg/L\)'
    # Matches the column where the note text can be found
    NOTES = '^Notes'
    # Matches headline of S concentrations
    S_VALUE = 'S ≤'
    # Matches headline of R concentrations
    R_VALUE = 'R >'
    # Specifies superscript tag which was added during vba preprocessing
    SS_TAG = '§'
    # Matches new numbered notes
    PNT = '(^\d|\n\d)(/\w)?.? '
    # Matches all Streptococcus subgroups
    STREP = '(?<=\s)[A-G](?=\s|$|,)'
    # Pattern to split entries separated by 'and' or comma
    SEP = ',|and'


# Regular experession patterns used while processing exceptions to breakpoints
class ExcRegex(Enum):
    # Matches exceptions which only contain of a single organism
    SNG = '^((\w\.\s\w*)|(\w*\s\w*.))$'
    # Matches all occurrences of Streptooccus groups
    STREP = 'Streptococcus(\sgroups)?(\s\w,)*(\s\w(\sand\s\w)?)?'
    # Splits all restrictions which contain more than one species into a list of species
    COMP = ',\s?|\sand\s'


# Regular experession patterns used while processing entries containing the compound name
class CmpRegex(Enum):
    # Matches all parentheses unless their content starts with except (in this case it is a species
    #  exception and should be dealt with in the subsequent analysis steps
    PAR = '\((?!except).*?\)'
    # Matches superscript containing one or more digits separated by comma or
    #  a dot (typo in the tables)
    SS = '§?(\d)(,\d)*(\.\d)*'
    # Matches the route of indication (roa or iv if they are separate words)
    ROA = '(?<=\s)(oral)|(?<=\s)(iv)'
    # Matches the compound name as the first word or first two words in case second word is 'acid'
    CMP = '^(\w|-)*( acid)?'
    # Matches superscript that contains 'HE'
    HE = '§?HE,?'


# Regular experession patterns which match irrelevant comments with minor
#  text changes to previous versions.
class NoteRegex(Enum):
    all_patterns = ["^Breakpoints are based on high dose therapy ?\(''.+\)?\.$",
                    "^Breakpoints are based on high dose therapy, "
                    "see table of dosages( ?\(.+\))?\.$",
                    "^For (\w|\s)*, see table of dosages\.$",
                    "^For more information, see .*\.$",
                    "^For susceptibility testing purposes, the concentration"
                    "(\s|\w)* is fixed at (\d)* mg/L\.$",
                    "^Agar dilution is the reference method for (\s|\w)*\.$",
                    "(((\s|\w)*\.\s)|^(\w|\s)*)MICs must be determined in the "
                    "presence ",
                    "of.*\((.*\))?\.(\s)*Follow the manufacturer('s|s') "
                    "instructions for commercial systems\.$",
                    "^For .* determination, the medium must be prepared fresh "
                    "on the day of use\.$",
                    "^(\s|\w)*(:|-)(\s|\w)* in the ratio \d*:\d*\. ",
                    "Breakpoints are expressed as the (\s|\w)* "
                    "concentration\.$",
                    "^(\w|\s)*breakpoints are based on once-daily"
                    "administration\.$]"]


class Info(Enum):
    # All information in parentheses found to be irrelevant for the analysis
    IRR_PAR = ['screen', 'test for high-level streptomycin resistance',
               'test for high-level aminoglycoside resistance']
    # All breakpoint types which are not backed by enough evidence or are not applicable
    #  and are consequently filtered out
    UNC = ['IE', 'NA', 'IP']
    # All known restrictions to a specific indication
    IND = ['meningitis', 'UTI', 'uncomplicated UTI', 'pneumonia',
           'prophylaxis for meningococcal disease',
           'prophylaxis for meningitis']
    # Title of sheets in the Eucast Clinical Breakpoint Tables which contain only general
    # information and are consequently not parsed
    GEN_SHEETS = ['Dosages', 'Tabelle1', 'Sheet1', 'Content', 'Notes',
                  'Guidance', 'Technical uncertainty', 'Changes',
                  'Topical agents', 'PK PD breakpoints']
    # List of all Isoxazyl agents
    ISOXAZYL = ['Oxacillin', 'Cloxacillin', 'Dicloxacillin', 'Flucloxacillin']
    # List of all agents with BL-inhibitor
    INH = ['Amoxicillin-clavulanic acid', 'Piperacillin-tazobactam', 'Ampicillin-sulbactam',
           'Ticarcillin-clavulanic acid']
    # List of all compound classes covered by the Eucast Breakpoint Tables
    CMP_CLASS = ['Penicillins', 'Carbapenems', 'Monobactams', 'Fluoroquinolones',
                 'Aminoglycosides', 'Lipoglycopeptides', 'Tetracyclines', 'Glycopeptides',
                 'Macrolides', 'Lincosamides', 'Oxazolidinone', 'Cephalosporins']
    # List of all agents that do not belong to any compound class
    UNCLASS = ['Chloramphenicol', 'Colistin', 'Daptomycin', 'Fosfomycin', 'Fusidic acid',
               'Metronidazole', 'Nitrofurantoin', 'Nitroxoline', 'Rifampicin', 'Spectinomycin',
               'Trimethoprim', 'Trimethoprim-sulfamethoxazole']
    # List of all compound classes whose members are Beta bactam agents.
    BLA = ['Penicillins', 'Carbapenems', 'Cephalosporins', 'Monobactams']


# Text to be logged or printed in case of any changes to previous versions or unexpected input
class OutText(Enum):
    CHOICE = '{} new comments were found during the parsing. Would you like to' \
             ' classify them directly in the console (a) ' \
             'or save them and edit the information manually (b): \n'
    NOANS = "Only 'a' (console) or 'b' (save out) are valid answers. " \
            "New comments were saved as 'missing_notes.xlsx' in the output " \
            "folder of the package."
    NPATH = "The path to the {} could not be found, please specify it in " \
            "the console:\n"
    GCLASS = 'Does this comment\n' \
             '(a) contain any information about how to derive the resistance ' \
             'phenotype from other resistances or susceptibilities (interpretive' \
             ' rules)?\n' \
             '(b) explicitly say that the species can be considered resistant?\n' \
             '(c) contain any information about the route of administration?\n' \
             '(d) contain any information about the indication the agent should be ' \
             'used for? \n' \
             '(e) contain any information about a species that is excepted from the ' \
             'general rule?\n' \
             '(f) contain a complete breakpoint including information about species,' \
             'compound and MIC?\n' \
             '(g) not add any information that can be directly encoded in the table?\n' \
             'Choice (a/b/c/d/e/f/g): '
    ROA = 'Please provide the route of administration (oral/iv/topical/nasal): '
    IND = 'Please provide the indication the agent may be used or should not be' \
          ' used as follows: "meningitis" or "NOT meningitis":'
    EXC = 'Please provide the excepted species: '
    BP = 'Please provide the information in the following format:\n"species; compound;' \
         ' S; R", if two thresholds are provided, otherwise "species; compound; S": '
    INV = 'Your choice was not valid. The note was now classified as not directly ' \
          'encodable in the table. If you want to revise this classification consult the ' \
          '"missing_notes.xlsx" file in the output folder and the Readme.'
    NOT_FOUND = 'comments which were not yet classified were found. Do you want to\n' \
                '(a) classify them via the console directly or \n(b) save comments into the ' \
                '"missing_notes.xlsx" file to be categorized manually.'
    CONS = 'The notes will be categorized in the console'
    MAN_CLASS = 'The notes were saved in the "missing_notes.xlsx" file and the program ' \
                'will be stopped. Please consult the Readme for more information ' \
                'about the classification.'
    WRONG_CLASS = 'A comment you classified as important was not classified in any of' \
                  ' the categories. Please consult the readme for further info'
    CHANGES = 'There were changes in the interpretive rules derived from the note text of ' \
              'the file. These changes rules can be looked up in the ' \
              '"interpretive_rule_changes.xlsx" file in the resource folder and have to ' \
              'be applied to the RuleBasedEngine.py manually'
    MAKE_STD = 'Do you want to save this classifications as new standards for all future' \
               ' classifications of this notes (a) or use the classifications only for this ' \
               'analysis and classify the comment manually later on (b).'
    NEW_PATH = 'Please provide the path to the desired output folder: '
    COL_CHECK = 'Please ensure that your input table contains the following ' \
                'columns: {}. \nYour table currently contains: {}'
    C_WARN = 'Warning: Table "{}" seems to have changes in the column structure. ' \
             'Headline "MIC breakpoint (mg/L)" was not found in column {}.'
    S_COLS = '"organism", "cmp_name","MIC" and "sample_id"'
    C_COLS = '"organism", "cmp_name" and "MIC"'
    BP_COLS = '"organism" and "cmp_name"'
    INC_BP = 'There was en error during the processing of Sheet {}, block ' \
             '{}. One of the breakpoints seems to be incomplete.{}'
    N_QC = 'There was an error during note processing for {}, block {}: The ' \
           'note text only contains {} entry/entries, but the highest ' \
           'detected superscript is {}.'
    REL = 'May this information relevant for further breakpoint' \
          ' classification? (y/n)'
    YON = 'Please answer only with "y" or "n". ' \
          'The comment was now considered relevant'
    N_ABB = 'Warning: A new organism name was found which could not be translated:' \
            ' {0}. Please consult the readthedocs on how to add it to the ' \
            'respective document.'
    N_WARN = 'Warning: Note block was not found in sheet "{}, line {}".'
    B_WARN = 'First block was not found in sheet "{}".'
    STR_WARN = 'Warning: Table "{}" seems to have changes in the ' \
               'column structure. Headline "{}" was not found in column {}.'
    M_CMP = 'Warning: The following compounds were not found in the compound ' \
            'dictionary: {}. Please consult the readthedocs for further ' \
            'information.'
    M_TAX = 'Warning: The following organisms could not be matched against the NCBI ' \
            'taxonomy:\n {}.\nPlease consult the readthedocs for further ' \
            'information.'
    NA_ORG = 'A problem occurred during parsing: Some breakpoints are not ' \
             'applicable to any organisms. '
    N_INF = 'A new type of information was found which could not be ' \
            'categorised : "{0}"\nPlease consult the readthedocs for more information.'
    ANA_TYPE = 'The analsys type "{}" is unknown. The table will be returned' \
               ' in a standard format.'
    INCOMPATIBLE = 'Error: The engine came to incompatible results ({}/{}) for "{}" regarding {}.'
    DIFFERENT = 'Warning: The engine came to different results ({}) than the AST ({}) ' \
                'for "{}" regarding "{}".'
    DUP = 'Warning: {} duplicated entries were found: {}'
    INT_CHANGES = 'There have been changes in the applicability of the interpretive rules' \
                  ' since the last version. Please consult the readthedocs on how to implement ' \
                  'them manually.'
    NAN = 'Error: Some of the organisms or compounds in the query table are NaN.'


def read_in_reference_dict(name):
    """
    Reads in phenotypical groups or compound class reference dictionaries.
    :param name: Name of the dictionary (phen_groups/cmp_classes)
    :type: String
    :return: Refernce dictionary
    :rtype: Dictionary
    """
    raw_table = pd.DataFrame
    if name == 'phen_groups':
        raw_table = pd.read_excel(Path.PHEN_G.value, sheet_name=None)
    elif name == 'cmp_classes':
        raw_table = pd.read_excel(Path.C_CLASS.value, sheet_name=None)
    reference_dict = dict()
    for title, sheet in raw_table.items():
        if len(sheet) > 0:
            reference_dict[list(sheet)[0]] = sheet.loc[:, list(sheet)[0]]
    return reference_dict
