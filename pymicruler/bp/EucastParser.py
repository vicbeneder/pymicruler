import pandas as pd
import re
import sys

from pymicruler.utils import util
from pymicruler.bp.BlockProcessor import BlockProcessor as BP
from pymicruler.bp.BlockInterpreter import BlockInterpreter as BI
from pymicruler.bp.NoteAnalysis import NoteAnalysis as NA
from pymicruler.bp.TaxonomyHandler import TaxonomyHandler as TH
from pymicruler.bp.ResourceCompiler import ResourceCompiler as RC


class EucastParser:
    def __init__(self):
        self.ires = pd.read_csv(util.Path.IRES.value)

        self.note_analyser = NA()
        self.b_i = BI()
        self.r_c = RC()
        self.all_sheets = pd.DataFrame()
        self.table = pd.DataFrame()
        self.guidelines = pd.DataFrame()

    def run_eucast_parser(self, bp_path):
        """
        Starts the parsing workflow for a given Eucast breakpoint table.

        :param bp_path: Path to Eucast breakpoint table.
        :type: String
        :return: Parsed breakpoints
        :rtype: Pandas DataFrame
        """
        self.all_sheets = pd.DataFrame()
        raw_table = pd.read_excel(
            bp_path, sheet_name=None, na_values=[''], keep_default_na=False)
        relevant_sheets = self._filter_sheets(raw_table)

        for title, sheet in relevant_sheets.items():
            organism = list(sheet)[0]
            note_col = self._column_check(sheet)
            reduced_sheet = self._column_removal(sheet, note_col)
            breakpoints = self._process_sheet(reduced_sheet, organism)
            self.all_sheets = pd.concat((self.all_sheets, breakpoints))

        self.note_analyser.summarize_note_analysis()
        self.table = self.b_i.run_block_interpreter(
            self.all_sheets, self.note_analyser)
        TH.run_quality_check(self.table)
        TH.run_quality_check(self.ires)
        out_table = self.r_c.run_compilation(self.table, self.ires)
        return out_table

    @staticmethod
    def _filter_sheets(table):
        """
        Removes sheets that do not contain breakpoints.

        :param table: The parsed EUCAST clinical breakpoint table.
        :type: Ordered Dictionary.
        :return: Table containing only relevant sheets.
        :rtype: Ordered Dictionary
        """
        sheets = set(table.keys())
        remove_sheets = sheets.intersection(set(util.Info.GEN_SHEETS.value))
        [table.pop(k) for k in remove_sheets]
        return table

    @staticmethod
    def _column_removal(sheet, note_col):
        """
        Removes all columns that do not contain information for AST
        interpretation.

        :param sheet: Currently processed sheet of the EUCAST breakpoint table.
        :type: Pandas Dataframe.
        :param note_col: Column index of note text
        :type: Integer
        :return: Reduced table containing compound, R_value, S_value and Notes.
        """
        relevant_cols = [k.value for k in util.ColPosStd]
        relevant_cols.append(note_col)
        sheet = sheet.iloc[:, relevant_cols]
        sheet.columns = util.Cols.BP_OUT.value
        return sheet

    def _process_sheet(self, sheet, organism):
        """
        Detects blocks within sheet, initializes analyses and returns
        information.

        :param sheet: One sheet of the Eucast breakpoint table
        :type: Pandas DataFrame
        :param organism: Name of the organism the breakpoints are applicable to
        :type: String
        :return: Dataframe with ordered breakpoint information
        :rtype: Pandas DataFrame
        """
        all_breakpoints = pd.DataFrame()
        block_starters = self._get_blocks(sheet)
        for idx in range(len(block_starters)-1):
            block = sheet.iloc[block_starters[idx]:block_starters[idx+1]]
            bp = BP()
            breakpoints = bp.process_block(block, organism, self.note_analyser)
            all_breakpoints = pd.concat((all_breakpoints, breakpoints))

        breakpoints = self._analyse_last_block(sheet, block_starters[-1],
                                               organism)
        all_breakpoints = pd.concat((all_breakpoints, breakpoints))

        return all_breakpoints

    def _analyse_last_block(self, sheet, block_idx, organism):
        """
        Finds last breakpoint within block and removes the following free text before
        starting the analysis.

        :param sheet: One sheet of the Eucast breakpoint table
        :type: Pandas DataFrame
        :param block_idx: The row index of the lasz block of the sheet
        :type: Integer
        :param organism: Name of the organism the breakpoints are applicable to
        :type: String
        :return: Dataframe with ordered breakpoint information
        :rtype: Pandas DataFrame
        """
        counter = 0
        last_idx = sheet.tail(1).index.item()
        for idx, row in sheet.iloc[block_idx:, 0].iteritems():
            if pd.isna(row):
                if counter > 2:
                    last_idx = idx
                    break
                else:
                    counter += 1
            elif re.search('for beta-lactam resistance', row) is not None:
                last_idx = idx-1
                break
            else:
                counter = 0

        bp = BP()
        block = sheet.iloc[block_idx: last_idx+1]
        breakpoints = bp.process_block(block, organism, self.note_analyser)
        return breakpoints

    @staticmethod
    def _get_blocks(sheet):
        """
        Find all indexes where a new block starts.

        :param sheet: One sheet of the Eucast breakpoint table
        :type: Pandas DataFrame
        :return: Indices of new blocks
        :rtype: List
        """
        sheet_filtered = sheet.iloc[:, util.ColPosStd.MIC.value]
        all_blocks_mask = sheet_filtered.str.contains(util.Regex.MIC.value, na=False)

        all_blocks = sheet.loc[all_blocks_mask].index

        return all_blocks

    def _column_check(self, sheet):
        """
        Checks if column structure matches expectaions.

        :param sheet: Currently processed sheet.
        :type: Pandas Dataframe.
        """
        idx = None
        r_val = None
        s_val = None

        title = list(sheet)[0]
        mic = util.ColPosStd.MIC.value

        if not sheet.iloc[:, util.ColPosStd.MIC.value].str.\
                contains(util.Regex.MIC.value).any():
            print(util.OutText.C_WARN.value.format(title, mic))
            sys.exit(1)

        else:
            for idx in range(sheet.shape[0]):
                if pd.notna(sheet.iloc[idx, util.ColPosStd.MIC.value]):
                    if re.match(util.Regex.MIC.value, sheet.iloc[idx, mic]):
                        idx_1 = idx + 1
                        r_val = sheet.iloc[idx_1, util.ColPosStd.R.value]
                        s_val = sheet.iloc[idx_1, util.ColPosStd.S.value]
                        break

        if re.match(util.Regex.R_VALUE.value, r_val) is None:
            print(util.OutText.STR_WARN.value.format(
                title, util.Regex.R_VALUE.value, mic))
            sys.exit(1)

        if re.match(util.Regex.S_VALUE.value, s_val) is None:
            print(util.OutText.STR_WARN.value.format(
                title, util.Regex.R_VALUE.value, mic))
            sys.exit(1)

        note_col = self._find_notes(sheet, idx, title)
        return note_col

    @staticmethod
    def _find_notes(sheet, row_idx, title):
        """
        Returns the column index of the note text for the analysed sheet.

        :param sheet: Currently processed sheet of Eucast breakpoint table.
        :type: Pandas DataFrame
        :param row_idx: Index of row where note column is expected.
        :type: Integer
        :param title: Title of currently processed sheet.
        :type: String
        :return: Column index of the note text
        :rtype: Integer
        """
        col_idx = None

        if row_idx is None:
            print(util.OutText.B_WARN.value.format(title))
            sys.exit(1)

        for idx, entry in sheet.iloc[row_idx].items():
            if pd.isna(entry):
                continue
            elif re.match(util.Regex.NOTES.value, entry):
                col_idx = sheet.columns.get_loc(idx)
                break

        if col_idx is None:
            print(util.OutText.N_WARN.value.format(title, row_idx+1))

        return col_idx
