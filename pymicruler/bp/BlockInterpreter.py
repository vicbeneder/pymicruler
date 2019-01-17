import pandas as pd
import numpy as np
import re
import sys

from pymicruler.utils import util


class BlockInterpreter:
    def __init__(self):
        self.phen_groups = util.read_in_reference_dict('phen_groups')
        self.translations = pd.read_excel(util.Path.RENAME.value)
        self.table = pd.DataFrame()
        self.note_ana = np.NaN

    def run_block_interpreter(self, table, note_analysis):
        """
        Processes all information within one block (= one compound class).

        :param table: One processing unit of the sheet dealing with one compound class
        :type: Pandas DataFrame
        :param note_analysis: Instance of Class NoteAnalysis
        :type: Instance of Class NoteAnalysis
        :return: Processed block
        :rtype: Pandas DataFrame
        """
        self.note_ana = note_analysis
        self.table = table.reset_index(drop=True)
        self.table['drop_row'] = np.NaN
        self.table['indication'] = np.NaN

        self._filter_uncertain_entries()
        self._convert_dashed_entries()
        self._process_notes()
        self._process_parentheses()
        self._process_restrictions()
        self._split_orgs()
        self._replace_phen_groups()
        self.note_ana.assess_interpretive_rule_changes()
        return self.table

    def _filter_uncertain_entries(self):
        """
        Filters out all guidelines that are marked as 'uncertain' by EUCAST.
        """
        indices = self.table.apply(lambda x: all(x in util.Info.UNC.value
                          for x in [x.r_value, x.s_value]), axis=1)
        self.table = self.table[~indices]

    def _convert_dashed_entries(self):
        """
        Converts all entries to resistant which do not have any note text assigned directly to them.
        """
        mask = self.table.apply(lambda x: self._check_if_convertable(x), axis=1)
        [self._convert_to_resistant(x) for x in mask.index]

    def _check_if_convertable(self, row):
        """
        Filters all entries that can be converted to resistant
        :param row: one row of the breakpoint table
        :type: Pandas Series
        :return: Boolean if row can be converted to resistant
        :rtype: Boolean
        """
        dashed = row.r_value == '-' and row.s_value == '-'
        all_ss = pd.isna(row.all_ss)
        all_relevant_ss = pd.isna(row.r_ss) and pd.isna(row.s_ss) and pd.isna(row.cmp_ss)
        return dashed and (all_ss or all_relevant_ss)

    def _process_restrictions(self):
        """
        Analyses any restriction to the applicability of the guideline to specific organisms.
        """
        exception_table = self.table[pd.notna(self.table.restrictions)]
        self.table = self.table[pd.isna(self.table.restrictions)]
        self.table = self.table.reset_index(drop=True)

        for idx, row in exception_table.iterrows():
            # match streptococcus groups:
            match = re.search(util.ExcRegex.STREP.value, row.restrictions)
            if match is not None:
                self._translate_streptococcus(idx, row.restrictions, exception_table)
                continue

            # match single species restriction:
            match = re.search(util.ExcRegex.SNG.value, row.restrictions)
            if match is not None:
                exception_table.loc[idx, 'organism'] = row.restrictions
                self.table = self.table.append(exception_table.loc[idx],
                                               verify_integrity=True,
                                               ignore_index=True)
                continue

            # match composed restrictions
            entry = row.restrictions.replace('\n', '')
            components = re.split(util.ExcRegex.COMP.value, entry)
            self._duplicate_rows(idx, exception_table, components)

    def _process_parentheses(self):
        """
        Analyses content encoded between parenthesis in the compound column.
        """
        self.table = self.table.reset_index(drop=True)
        par = self.table[pd.notna(self.table.parenthesis)]
        for idx, row in par.iterrows():
            # parenthesis only contains indication
            if row.parenthesis in util.Info.IND.value:
                self.table.at[idx, ['parenthesis',
                                    'indication']] = (np.NaN, row.parenthesis)
                continue
            # parenthesis contains irrelevant information
            if row.parenthesis in util.Info.IRR_PAR.value:
                self.table.at[idx, 'parenthesis'] = np.NaN
                continue

            # exclusion of a specific indication
            match = re.split('other than ', row.parenthesis)
            if len(match) > 1:
                self.table.at[idx, ['parenthesis',
                                    'indication']] = (np.NaN, 'NOT '+match[1])
                continue

            # restriction to specific indication
            match = re.split(' only', row.parenthesis)
            if len(match) > 1:
                self.table.at[idx, ['parenthesis',
                                    'indication']] = (np.NaN, match[0])
                continue
            print(util.OutText.N_INF.value.format(row.parenthesis))

    def _detect_exceptions(self, org):
        """
        Detects and processes any exceptions to the guideline.

        :param org: Entry decribing the organism the guideline is applicable to
        :type: String
        :return: The name of the organism and any exceptions that were detected
        :rtype: String, String
        """
        exception = re.split('except\s|\sother\sthan\s', org)
        if len(exception) > 1:
            org_exception = exception[1].strip(' (),')
            org_exception = self._translate_abbreviations(org_exception)
            org = exception[0].strip(' (),')
        else:
            org_exception = None
        return org, org_exception

    def _duplicate_rows(self, idx, table, org_list):
        """
        Adds copies of guidelines which were applicable to multiple organisms.

        :param idx: row index of the guideline that should be duplicated
        :type: Integer
        :param table: Data table containing the guideline
        :type: Pandas DataFrame
        :param org_list: The list of organisms the row is applicable to
        :type: List
        """
        row = table.loc[idx].copy()
        for org in org_list:
            org, exc = self._detect_exceptions(org)
            row.loc['organism'] = org
            if exc is not None:
                row.loc['exception'] = exc
            self.table = self.table.append(row, verify_integrity=True, ignore_index=True)

    def _process_notes(self):
        """
        Splits note text into individual notes and starts the analysis.
        """
        self.table = self.table.reset_index(drop=True)
        notes = self.table[pd.notna(self.table.all_ss)]
        for idx, row in notes.iterrows():
            note_list = re.split('\n>', row.note_text)
            numbers = row.all_ss.split(', ')
            for num in numbers:
                note_info = self.note_ana.get_note_information(note_list[int(
                    num)-1], row.organism, row.cmp_name)
                self._analyse_note_info(note_info, idx)
        self.table = self.table[self.table.drop_row != 1]

    def _analyse_note_info(self, info_dict, idx):
        """
        Analyses the information about the content of the note text.

        :param info_dict: dictionary containing information about the meaning of a note.
        :param idx: row index the note is applicable for.
        :type: Integer
      """
        if info_dict['relevance'] == 0:
            self._process_irrelevant_comments(idx)
            return
        if info_dict['no_resistance'] == 1 \
                or info_dict['interpretation'] == 1 \
                or info_dict['not_encodable'] == 1:
            self._drop_idx(idx)
            return
        if pd.notna(info_dict['exception']):
            self._save_new_info(idx, info_dict['exception'], 'exception')
        if pd.notna(info_dict['roa']):
            self._save_new_info(idx, info_dict['roa'], 'roa')
        if pd.notna(info_dict['indication']):
            self._save_new_info(idx, info_dict['indication'], 'indication')
        if pd.notna(info_dict['resistance']):
            self._convert_to_resistant(idx)
        if pd.notna(info_dict['new_bp']):
            self._add_new_bp(info_dict['new_bp'])
            self._convert_to_resistant(idx)

    def _convert_to_resistant(self, idx):
        """
        Converts all remaining dashed entries to resistant.

        :param idx: row index of the guideline that should be duplicated
        :type: Integer
        """
        if self.table.loc[idx, ['r_value', 's_value']].all() == '-':
            self.table.loc[idx, ['r_value', 's_value']] = (0, -1)

    def _process_irrelevant_comments(self, idx):
        """
        Drops or converts rows that have comments which are found to be irrelevant.

        :param idx: row index of the guideline the comment is applicable to.
        :type: Integer
        """
        if self.table.loc[idx, ['s_value', 'r_value']].all() == 'Note':
            self.table.loc[idx, 'drop_row'] = 1
        else:
            self._convert_to_resistant(idx)

    def _drop_idx(self, idx):
        """
        Drops entries if the r- and s-value are either Note or '-*.

        :param idx: index of the row to be analysed
        :type: Integer
        """
        if self.table.loc[idx, ['s_value', 'r_value']].all() in ['-', 'Note']:
            self.table.loc[idx, 'drop_row'] = 1

    def _save_new_info(self, idx, text, column):
        """
        Saves information derived from the note text to the respective columns.

        :param idx: row index of the guideline the comment is applicable to.
        :type: Integer
        :param text: new information that should be saved
        :type: String
        :param column: name of the column the information should be save in
        :type: String
        """
        if pd.isna(self.table.loc[idx, column]):
            self.table.loc[idx, column] = text
        elif text != self.table.loc[idx, column]:
            print('overlap', self.table.at[idx, column], text)

    def _add_new_bp(self, text):
        """
        Adds a new breakpoint base don information derived from the notes.

        :param text: Breakpoint information as derived from the interpretation dict.
        :type: String
        """
        bp = text.split('; ')
        new_row = {
            'organism': bp[0],
            'cmp_name': bp[1],
            's_value': bp[2]
        }
        new_row['r_value'] = bp[3] if len(new_row) > 3 else bp[2]
        self.table = self.table.append(new_row, verify_integrity=True,
                                       ignore_index=True)

    def _replace_phen_groups(self):
        """
        Detects phenotypically defined groups and duplicates entries for all member species.
        """
        for key in self.phen_groups.keys():
            mask = self.table.organism.str.contains(key, flags=re.IGNORECASE, regex=True)
            phen = self.table[mask]
            if len(phen) > 0:
                self.table = self.table[~mask]
                species_list = self.phen_groups[key].copy().tolist()
                existing_bps = self._find_existing_breakpoints(phen, species_list)
                if existing_bps is not None:
                    cmp_groups = existing_bps.groupby('cmp_name')
                    for name, group in cmp_groups:
                        organisms = group.organism.unique()
                        updated_list = species_list.copy()
                        [updated_list.remove(x) for x in organisms]
                        row_idx = phen[phen.cmp_name == name].index[0]
                        self._duplicate_rows(row_idx, phen, updated_list)
                        phen = phen[phen.cmp_name != name]
                for idx, row in phen.iterrows():
                    self._duplicate_rows(idx, phen, species_list)

    def _find_existing_breakpoints(self, df, phen_list):
        """
        Checks if any of the member species has an own entry in the table already.

        :param df: All breakpoints that need to be duplicated for a specific
         phenotypically defined group.
        :type: Pandas DataFrame
        :param phen_list: A list of member species that make up the phenotypically defined group.
        :type: List
        :return: Existing entries or None
        :type: Pandas DataFrame
        """
        compounds = df.cmp_name.unique()
        mask = self.table.organism.isin(phen_list) & self.table.cmp_name.isin(compounds)
        if sum(mask) == 0:
            return None
        else:
            return self.table[mask]

    def _translate_streptococcus(self, idx, entry, table):
        """
        Splits name into individual subgroups groups (A, B, C and G).

        :param idx: row index of the guideline that should be duplicated
        :type: Integer
        :param entry: Entry containing groups of Streptococcus
        :type: String
        :param table: Data table containing the guideline
        :type: Pandas DataFrame
        """
        match = re.findall(util.Regex.STREP.value, entry)
        org_list = ['Group ' + x for x in match]
        self._duplicate_rows(idx, table, org_list)

    def _split_orgs(self):
        """
        Process organism names for multiple entries and abbreviations.
        """
        # Translate streptococcus groups
        mask = self.table.organism.str.contains('Streptococcus groups', na=False)
        strep = self.table[mask].reset_index(drop=True)
        self.table = self.table[~mask].reset_index(drop=True)
        for idx, row in strep.iterrows():
            self._translate_streptococcus(idx, row.organism, strep)

        # Split two species within one entry
        mask = self.table.organism.str.contains(util.Regex.SEP.value,
                                                regex=True, na=False)
        sep = self.table[mask].reset_index(drop=True)
        self.table = self.table[~mask].reset_index(drop=True)
        for idx, row in sep.iterrows():
            components = re.split(util.ExcRegex.COMP.value, row.organism)
            components[1] = components[0].split(' ')[0] + ' ' + components[1]
            self._duplicate_rows(idx, sep, components)

        # Remove spp.
        self.table.organism = self.table.organism.apply(
            lambda x: x.replace(' spp.', '') if x is not None else None)

        # Translate all abbreviations
        self._check_for_renamed_species()

    def _translate_abbreviations(self, entry):
        """
        Translates any detected abbreviation to the organisms full name.
        :param entry: abbreviated organism name
        :type: String
        :return: Full name
        :rtype: String
        """
        try:
            translated = self.translations.loc[
                self.translations.query_term == entry, 'replacement'].iloc[0]
        except IndexError as e:
            print(util.OutText.N_ABB.value.format(entry), '\n', e)
            sys.exit(0)
        return translated

    def _check_for_renamed_species(self):
        """
        Searches all entries for names which are either short forms or have recently been
        renamed and renames them according to the NCBI Taxonomy.
        """
        all_orgs = self.table.organism.unique()
        for element in all_orgs:
            if element in self.translations.query_term.values:
                translated = self.translations.loc[
                    self.translations.query_term == element,
                    'replacement'].iloc[0]
                self.table.loc[self.table.organism == element,
                               'organism'] = translated
