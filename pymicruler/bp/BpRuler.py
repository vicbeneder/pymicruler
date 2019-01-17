import pandas as pd
from pymicruler.bp.TaxonomyHandler import TaxonomyHandler as TH
from pymicruler.bp import RuleBasedEngine
from pymicruler.utils import util

import numpy as np
import sys


class BpRuler:
    def __init__(self):
        self.resource = pd.DataFrame()
        self.unknown_entries = pd.DataFrame()
        pd.options.mode.chained_assignment = None

    def run_breakpoint_query(self, resource, query_table, ana_type='bp'):
        """
        Looks up breakpoints based on the provided guidelines and query table.

        :param resource: Path to parsed Eucast guidelines table.
        :type: String
        :param query_table: Data frame containing organisms and compounds to
        query
        :type: Pandas DataFrame
        :param ana_type: Type of analysis to indicate which columns are
        necessary. Default is breakpoint (bp).
        :type: String
        :return: Query table updated with result column.
        :rtype: Pandas DataFrame
        """
        self.resource = pd.read_excel(resource)
        self._prepare_query_data(query_table, ana_type)

        query_mask = self.sample.apply(
            lambda x: pd.isna(x.matched_organism) and pd.isna(x.matched_cmp_name),
            axis=1)

        self.sample[['s_value', 'r_value', 'matched_organism', 'matched_cmp_name']] = \
            self.sample[query_mask].apply(
                lambda x: pd.Series(self._bp_look_up(x.lineage, x.cmp_name)), axis=1)

        if ana_type == 'bp':
            output_table = self._prepare_output(ana_type)
            return output_table

    def run_sample_classification(self, resource, sample_data, ana_type='classify'):
        """
         Classifies AST results based on parsed Eucast guidelines.

        :param resource: Path to parsed Eucast guidelines
        :type: String
        :param sample_data: Data to be analysed containing analysed organism,
        compound names and MICs.
        :type: Pandas DataFrame
        :param ana_type: Type of analysis that is conducted. If called by
        user use default.
        :return: Orginal table updated with resistance classification
        :rtype: Pandas DataFrame
        """
        self.run_breakpoint_query(resource, sample_data, ana_type)
        self._run_classification()

        if ana_type == 'classify' \
                and pd.isna(self.sample.label).any() \
                and 'sample_id' in list(self.sample):

            rbe_df = self._reduce_to_incomplete_samples()
            results = RuleBasedEngine.run_rbe(rbe_df)

            self._process_classification_results_rbe(rbe_df, results)
            output_table = self._prepare_output(ana_type)

            return output_table

    def get_whole_resistance_phenotype(self, resource, sample_data):
        """
        Retrieves all resistance information that can be derived from the
        Eucast guidelines and interpretive rules.

        :param resource: Path to parsed Eucast guidelines
        :type: String
        :param sample_data: Data to be analysed containing analysed organism,
        compound names, MICs and sample IDs.
        :type: Pandas DataFrame
        :return: Table of all derived resistance phenotypes
        :rtype; Pandas DataFrame
        """
        ana_type = 'sample'

        self.run_sample_classification(resource, sample_data, ana_type)

        rbe_df = self.sample.groupby('sample_id')
        results = RuleBasedEngine.run_rbe(rbe_df)

        self._process_whole_phenotype(rbe_df, results)
        output_table = self._prepare_output(ana_type)

        return output_table

    def _prepare_query_data(self, sample, ana_type):
        """
        Prepares data for subsequent query.

        :param sample: Data to be analysed
        :type: Pandas DataFrame
        :param ana_type: Type of analysis that is conducted (bp/classify/full)
        :type: String
        """
        self.sample = sample
        self._column_qc(ana_type)

        self.sample['lineage'] = np.NaN
        self.sample.MIC = self.sample.MIC.astype(float)

        missing_orgs, missing_cmps = TH.run_quality_check(self.sample)
        if any((missing_cmps, missing_orgs)):
            self._handle_missing_information(missing_orgs, missing_cmps)

        self._get_taxids()
        self._get_lineages()

    def _column_qc(self, ana_type):
        """
        Checks if all necessary columns for the respective analysis are present.

        :param ana_type: Type of analysis that is conducted (bp/classify/full)
        :type: String
        """
        col_names = list(self.sample)

        if ana_type == 'sample':
            for x in util.Cols.ADDED_SMPL.value:
                self.sample[x] = np.NaN
            if any(x not in col_names for x in util.Cols.FULL.value):
                print(util.OutText.COL_CHECK.value.format(util.Cols.FULL.value, col_names))
                sys.exit(1)

        elif ana_type == 'classify':
            for x in util.Cols.ADDED_SMPL.value:
                self.sample[x] = np.NaN
            if any(x not in col_names for x in util.Cols.CLASS.value):
                print(util.OutText.COL_CHECK.value.format(util.Cols.CLASS.value, col_names))
                sys.exit(1)

        elif ana_type == 'bp':
            for x in util.Cols.ADDED_BP.value:
                self.sample[x] = np.NaN
            if any(x not in col_names for x in util.Cols.BP.value):
                print(util.OutText.COL_CHECK.value.format(util.Cols.BP.value, col_names))
                sys.exit(1)

    def _get_taxids(self):
        """
        Looks up TaxIDs for all organisms to be analysed
        """
        all_org_ids = TH.translate_all(self.sample.organism.unique())

        for key, value in all_org_ids.items():
            self.sample.loc[self.sample.organism == key, 'organism_id'] = value[0]

    def _handle_missing_information(self, orgs, cmps):
        """
        Marks entries where compound names or organism names could not be found.
        """
        if orgs is not None:
            mask = self.sample.apply(lambda x: x.organism in orgs, axis=1)
            self.unknown_entries = self.sample[mask]
            self.unknown_entries.matched_organism = 'Organism not found'
            self.sample = self.sample[~mask]

        if cmps is not None:
            mask = self.sample.apply(lambda x: x.organism in cmps, axis=1)
            unknown_entries = self.sample[mask]
            unknown_entries.matched_cmp_name = 'Compound not found'
            self.unknown_entries = pd.concat((self.unknown_entries, unknown_entries))
            self.sample = self.sample[~mask]

        self.sample = self.sample.reset_index(drop=True)

    def _get_lineages(self):
        """
        Looks up lineages for all organisms to be analysed
        """
        all_orgs = self.sample.loc[pd.isna(self.sample.matched_organism), 'organism_id'].unique()
        lineages = TH.get_all_lineages(all_orgs)

        self.sample = self.sample.astype('object')

        for org, lineage in zip(all_orgs, lineages):
            for idx, row in self.sample.loc[self.sample.organism_id == org].iterrows():
                self.sample.loc[idx, 'lineage'] = lineage

    def _bp_look_up(self, lineage, cmp_name):
        """
        Searches for applicable breakpoints for a given lineage and compound

        :param lineage: Taxonomic lineage of the queried organism
        :type: List
        :param cmp_name: Compound the organism was tested for
        :type: String
        :return: Result of query
        :rtype: Dictionary/None
        """
        for org in reversed(lineage):
            result = self.resource.query('organism == @org and cmp_name == @cmp_name')
            if len(result) > 0:
                result = result.iloc[0]
                if pd.notna(result['exception']) and result['exception'] in lineage:
                    continue
                else:
                    res = [float(result.s_value), float(result.r_value),
                           result.organism, result.cmp_name]
                    return res
        else:
            res = [None]*4
        return res

    def _run_classification(self):
        """
        Classifies AST result based on breakpoint and MIC.
        """
        for idx, row in self.sample.iterrows():
            if pd.isna(row.r_value):
                self.sample.loc[idx, 'label'] = np.NaN
            else:
                if row.MIC > row.r_value:
                    self.sample.loc[idx, 'label'] = 'R'
                elif row.MIC <= row.s_value:
                    self.sample.loc[idx, 'label'] = 'S'
                else:
                    self.sample.loc[idx, 'label'] = 'I'

    def _reduce_to_incomplete_samples(self):
        """
        Reduces the data set to only those samples with unclassified compounds.

        :return: DataFrame of incompletely analysed samples.
        :rtype: Pandas DataFrame
        """
        samples_for_rbe = self.sample[pd.isna(self.sample.label)].sample_id.unique()

        self.sample['incmplt'] = self.sample.apply(lambda x: x.sample_id in samples_for_rbe, axis=1)
        rbe_df = self.sample[self.sample.incmplt]

        groups = rbe_df.groupby('sample_id')
        return groups

    def _process_classification_results_rbe(self, rbe_df, results):
        """
        Analyses output of rule-based engine for compounds that were tested but could not be
        classified by means of a breakpoint.

        :param rbe_df: Incomplete data analysed in the rule based engine.
        :type: Pandas DataframeGroupby
        :param results: Results of the rule-based engine for each of the samples.
        :type: List
        """
        for group, result in zip(rbe_df, results):
            if len(result) > 0:
                for key, value in result.items():
                    if key in group[1].cmp_name.values:
                        pos = group[1][group[1].cmp_name == key].index
                        self.sample.loc[pos, 'label'] = value

    def _process_whole_phenotype(self, rbe_df, results):
        """
        Adds any new resistance labels found by the rule-based engine to the output table.

        :param rbe_df: Data analysed in the rule based engine
        :type: Pandas DataframeGroupby
        :param results: Results of the rule-based engine for each of the samples.
        """
        for group, result in zip(rbe_df, results):
            if len(result) > 0:
                for key, value in result.items():
                    if key in group[1].cmp_name.values:
                        pos = group[1][group[1].cmp_name == key].index
                        self.sample.loc[pos, 'label'] = value
                    else:
                        new_row = pd.Series({'organism': group[1].organism.iloc[0],
                                             'cmp_name': key,
                                             'label': value,
                                             'sample_id': group[1].sample_id.iloc[0]
                                             })
                        self.sample = self.sample.append(
                            new_row, ignore_index=True, verify_integrity=True)

    def _prepare_output(self, ana_type):
        """
        Reduce table to essential columns.
        :param ana_type: Type of analysis that was conducted (bp/class/sample)
        :type: String
        :return: Query results.
        :type: Pandas DataFrame
        """
        self.sample.loc[pd.isna(self.sample.matched_organism),
                        'matched_organism'] = 'Breakpoint not found'
        output_table = self.sample.drop(util.Cols.RULER_DROP_ELSE.value, axis=1)

        if ana_type == 'classify' and 'incmplt' in list(output_table):
            output_table = output_table.drop('incmplt', axis=1)

        if len(self.unknown_entries) > 0:
            output_table = pd.concat((output_table, self.unknown_entries), sort=False)

        return output_table
