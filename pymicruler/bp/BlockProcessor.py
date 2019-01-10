import sys
import re

import pandas as pd
import numpy as np

from pymicruler.utils import util


class BlockProcessor:
    def __init__(self):
        self.breakpoints = pd.DataFrame(columns=util.Cols.PROC.value)
        self.note_text = ''
        self.note_list = []
        self.block_he = 0
        self.compound_family_ss = np.NaN
        self.note_analysis = np.NaN
        self.compound_family = ''
        self.block = pd.DataFrame()
        self.organism = ''
        self.block_exception = np.NaN

    def process_block(self, block, sheet_title, note_analysis):
        """
        Processes information for one specific family of compounds.
        :param block: Breakpoint data
        :type: Pandas DataFrame
        :param sheet_title: Name of the current sheet (= name of the organism)
        :type: String
        :param note_analysis: Instance of the class NoteAnalysis
        :return: parsed and preliminarily ordered breakpoints
        :rtype: Pandas DataFrame
        """
        self.note_analysis = note_analysis
        self.compound_family = block.iloc[0, 0]

        self.block = block.iloc[2:].copy()
        self.organism = sheet_title

        self._process_organism()
        self._process_compound_family()
        self._locate_note_text()
        self._process_note_text()
        self._remove_empty_rows()
        self._process_body()
        self._process_superscript()
        self._note_qc()
        self._add_general_info()

        return self.breakpoints

    def _process_organism(self):
        """
        Analyses name of organism for any exceptions or special characters.
        """
        split = re.split('except ', self.organism)
        if len(split) > 1:
            self.block_exception = split[1]
            self.organism = split[0]
        self.organism = self.organism.strip('* \n')
        if self.organism.find('Enterobacteriaceae') != -1:
            self.organism = 'Enterobacterales'

    def _process_compound_family(self):
        """
        Categorises compounds without compound family as miscellaneous agents
        and checks for superscript.
        """
        if pd.isna(self.compound_family):
            self.compound_family = 'Miscellaneous agents'
            return

        self.compound_family, par, roa, ss, restriction, he = \
            self._process_compound(self. compound_family)
        self.compound_family = self.compound_family.replace('*', '')

        if pd.notna(ss):
            self.compound_family_ss = ss

        if pd.notna(he):
            self.block_he = True

    def _locate_note_text(self):
        """
        Locates the position of the note text and parses it.
        """
        notes = self.block.notes.astype(str).str.replace(u'\xa0', ' ')
        self.block.notes = notes.replace('nan', np.NaN)

        for idx, row in self.block.notes.iteritems():
            if pd.isna(row):
                continue
            elif re.search(util.Regex.PNT.value, row) is not None:
                self.note_text = row

    def _process_note_text(self):
        """
        Dissects note text in the individual notes and stores them in a list.
        """
        if pd.isna(self.note_text):
            return
        else:
            all_notes = self.note_text.split('\n')
            res = [re.match(util.Regex.PNT.value, x) for x in all_notes]
            for idx in range(len(res)):
                if res[idx] is None:
                    if all_notes[idx][:5].find('.') != -1:
                        continue
                    elif len(all_notes[idx].strip(' ,\n')) > 0:
                        entry = self.note_list[-1] + ' ' + all_notes[idx].strip(' ,\n')
                        self.note_analysis.check_if_known(entry)
                        self.note_list[-1] = entry
                else:
                    entry = all_notes[idx][res[idx].end():].strip(' ')
                    self.note_analysis.check_if_known(entry)
                    self.note_list.append(entry)

    def _remove_empty_rows(self):
        """
        Removes any blank lines within blocks.
        """
        self.block = self.block.dropna(axis='index', how='all')
        if self.block.cmp_name.isnull().any():
            self._handle_incomplete_rows()

    def _handle_incomplete_rows(self):
        """
        Analyses rows that are not empty but contain no compound name.
        """
        incmplt_rows = self.block[pd.isna(self.block.cmp_name)]

        for idx, row in incmplt_rows.iterrows():
            # if note text is split between two lines it is added to the notes
            if pd.notna(row.iloc[-1]):
                match = re.search(util.Regex.PNT.value, row.notes)
                if match is not None:
                    self.note_list.append(row.notes[match.end():].strip(' '))
                self.block.at[idx, 'notes'] = np.NaN
            # if r and s conc are dashed but no compound name is given it is
            # deleted
            elif row.r_value == '-' and row.s_value == '-':
                self.block.at[idx, 's_value'] = np.NaN
                self.block.at[idx, 'r_value'] = np.NaN

        self.block = self.block.dropna(axis='index', how='all')

        if pd.isna(self.block.cmp_name).any():
            print(util.OutText.INC_BP.value.format(
                    self.organism, self.compound_family, self.block.values))

    def _process_body(self):
        """
        Parses and analyses compound name, R- and S-concentrations
        and creates uniform table.
        """
        s_result = self.block.s_value.apply(
            lambda x: self._separate_superscript(x))
        s_result = pd.DataFrame(
            s_result.values.tolist(), columns=['s_value', 's_ss'])

        r_result = self.block.r_value.apply(
            lambda x: self._separate_superscript(x))
        r_result = pd.DataFrame(
            r_result.values.tolist(), columns=['r_value', 'r_ss'])

        compound_result = self.block.cmp_name.apply(
            lambda x: self._process_compound(x))
        compound_result = pd.DataFrame(
            compound_result.values.tolist(), columns=util.Cols.BODY.value)

        if self.block_he == 1:
            compound_result.high_exposure = 1

        if len(s_result) == len(r_result) == len(compound_result):
            self.breakpoints = pd.concat(
                (s_result, r_result, compound_result), axis=1, sort=False)
        else:
            print('An error ocurred during processing')
            sys.exit(1)

    @staticmethod
    def _separate_superscript(entry):
        """
        Separates r- and s-concentrations and superscript.

        :param entry: r- or s-concentrations as specified in the document
        :type: String
        :return: the separated concentration and superscript (if applicable)
        :rtype: list
        """
        if isinstance(entry, float) or isinstance(entry, int):
            return [entry, np.NaN]
        elif entry.find(util.Regex.SS_TAG.value) != -1:
            return entry.split(util.Regex.SS_TAG.value)
        else:
            return [entry, np.NaN]

    @staticmethod
    def _process_compound(entry):
        """
        Separates compound name from additional information such as superscript,
        exceptions or indications.

        :param entry: Compound name as specified in the EUCAST table.
        :return: cmp: compound name, par: content of parenthesis,
        roa: route of administration, ss: superscript, restriction: any
        information that restricts applicability, he: high exposure (dosis).
        :rtype: String or None
        """
        par = np.NaN
        roa = np.NaN
        ss = np.NaN
        he = np.NaN

        # content of parentheses
        match = re.search(util.CmpRegex.PAR.value, entry)
        if match is not None:
            par = match.group()[1:-1]
            entry = entry[:match.start()] + entry[match.end():]

        # information about the route of administration
        match = re.search(util.CmpRegex.ROA.value, entry)
        if match is not None:
            roa = match.group()
            entry = entry[:match.start()] + entry[match.end():]

        # indicator of high exposure
        match = re.search(util.CmpRegex.HE.value, entry)
        if match is not None:
            entry = entry[:match.start()] + entry[match.end():]
            he = 1

        # superscript
        match = re.search(util.CmpRegex.SS.value, entry)
        if match is not None:
            ss = match.group().strip('§,')
            entry = entry[:match.start()] + entry[match.end():]

        # separate any restrictions from compound name
        match = re.search(util.CmpRegex.CMP.value, entry)
        cmp = match.group()
        restriction = entry[:match.start()] + entry[match.end():].strip(' \n,')
        if len(restriction) < 1:
            restriction = np.NaN

        return cmp, par, roa, ss, restriction, he

    def _process_superscript(self):
        """
        Gathers all superscript notations used in different columns
        for the individual breakpoints.
        """
        if pd.notna(self.compound_family_ss):
            cmp_family_ss = set(self.compound_family_ss.split(','))
        else:
            cmp_family_ss = set()
        for idx, row in self.breakpoints[['r_ss', 's_ss', 'cmp_ss']].iterrows():
            all_ss = cmp_family_ss.copy()
            for element in row:
                if pd.notna(element):
                    element = element.replace('.', ',')
                    digits = element.split(',')
                    all_ss.update(digits)
            self.breakpoints.loc[idx, 'all_ss'] = ', '.join(all_ss) \
                if len(all_ss) > 0 else np.NaN

    def _note_qc(self):
        """
        Checks if a note text exists for every footnote specified in the block.
        """
        block_ss = set()
        self.breakpoints.all_ss.apply(
            lambda x: block_ss.update(x.split(', ')) if pd.notna(x) else None)
        if len(block_ss) == 0:
            return
        elif len(self.note_list) < float(max(block_ss)):
            print(util.OutText.N_QC.value.format(
                self.organism, self.compound_family, len(self.note_list),
                float(max(block_ss))))

    def _add_general_info(self):
        """
        Add block-wide information to the finished table.
        """
        self.breakpoints['cmp_family'] = self.compound_family
        self.breakpoints['organism'] = self.organism
        self.breakpoints['note_text'] = '\n>'.join(self.note_list)
        self.breakpoints['cmp_family_ss'] = self.compound_family_ss
        self.breakpoints['exception'] = self.block_exception
