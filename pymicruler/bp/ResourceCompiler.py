import pandas as pd
from pymicruler.utils import util


class ResourceCompiler:
    def __init__(self):
        self.dropped_entries = pd.DataFrame()
        self.ires = pd.DataFrame()
        self.bp_table = pd.DataFrame

    def run_compilation(self, bp_table, ires):
        """
        Compiles the breakpoint table with the intrinsic resistance table.

        :param bp_table: Parsed breakpoint table
        :type: Pandas DataFrame
        :param ires: Intrinsic resistance table
        :type: Pandas DataFrame
        :return: Compiled table
        :rtype: Pandas DataFrame
        """
        self.bp_table = bp_table.reset_index(drop=True)

        self.ires = ires
        self._prepare_tables()
        self._remove_oral_bp()
        self._remove_indication_bp()
        self._compile_bp_ires()
        self._final_duplication_check()

        out_table = self._prepare_output()
        return out_table

    def _prepare_tables(self):
        """
        Adds a column containing the type of guidelines ('bp'/'ires') and
        helper columns for organism-compound combinations.
        """
        self.bp_table['source'] = 'bp'
        self.ires['source'] = 'ires'

        self.bp_table['combination'] = self.bp_table.organism + ' ' + self.bp_table.cmp_name
        self.ires['combination'] = self.ires.organism + ' ' + self.ires.cmp_name

    def _remove_oral_bp(self):
        """
        Removes all breakpoints with oral route of administration.
        """
        self.bp_table['roa_dup'] = self.bp_table[['combination']].duplicated(keep=False)

        roa_dups = self.bp_table.query('roa_dup == True and roa == "oral"')
        self.bp_table = self.bp_table.query('roa_dup == False or roa != "oral"')

        self.bp_table.reset_index(drop=True)
        self.dropped_entries = roa_dups

    def _remove_indication_bp(self):
        """
        Removes all duplicate entries that are restricted to specific indications.
        """
        self.bp_table['ind_dup'] = self.bp_table[['combination', 'roa']].duplicated(keep=False)
        self.bp_table['ind_only'] = self.bp_table.apply(
            lambda x: x.indication in util.Info.IND.value, axis=1)

        dups = self.bp_table.query('ind_dup == True and ind_only == True')
        self.bp_table = self.bp_table.query('ind_dup == False or ind_only == False')

        pd.concat((self.dropped_entries, dups), axis=0, sort=False)
        self.bp_table.reset_index(drop=True)

    def _compile_bp_ires(self):
        """
        Merge information on intrinsic resistance with breakpoint table.
        Check for duplicates covered in ires and breakpoint files.
        In these cases only breakpoint data is kept.
        """
        self.compile = pd.concat([self.bp_table, self.ires], sort=True)
        self.compile.reset_index(drop=True, inplace=True)

        duplicates = self.compile[self.compile.combination.duplicated(keep=False)]

        neg = duplicates[duplicates.source == 'ires']

        self.compile.drop(neg.index, inplace=True)
        self.compile.reset_index(drop=True, inplace=True)

    def _final_duplication_check(self):
        """
        Ensures that only one guideline is applicablw to each species-compound combinations.
        """
        dups = self.compile[self.compile.combination.duplicated(keep=False)]

        if len(dups) > 0:
            print(util.OutText.DUP.value.format(
                len(dups) / 2, dups[['combination', 'roa', 'indication']].values))

    def _prepare_output(self):
        """
        Reduction of columns to essential information.

        :return: Essential columns of the parsed table
        :rtype: Pandas DataFrame
        """
        output = self.compile[util.Cols.PARS_OUT.value].copy()
        output.r_value = output.r_value.astype(float)
        output.s_value = output.s_value.astype(float)
        return output
