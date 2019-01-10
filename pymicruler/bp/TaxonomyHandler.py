import sys
import pandas as pd

from ete3 import NCBITaxa

from pymicruler.utils import util


class TaxonomyHandler:
    @staticmethod
    def run_quality_check(table):
        """
        Analyses if all organisms and compounds are known.

        :param table: Parsed Eucast breakpoint table.
        """
        if sum(pd.isna(table.organism.unique())) + sum(pd.isna(table.cmp_name.unique())) > 0:
            print(util.OutText.NAN.value)
            sys.exit(0)

        missing_organism = TaxonomyHandler._check_organism(table.organism.unique())
        missing_compounds = TaxonomyHandler._check_compounds(table.cmp_name.unique())

        if 'exception' in list(table):
            TaxonomyHandler._check_organism(table[pd.notna(
                table.exception)].exception.unique())
        return missing_organism, missing_compounds

    @staticmethod
    def get_all_lineages(all_orgs):
        """
        Looks up lineages for an array of organisms.

        :param all_orgs: All organisms that are queried.
        :type: Numpy ndarray
        :return: lineages (names) for all organisms.
        rtype: List
        """
        all_names = []

        ncbi = NCBITaxa()

        lineages = [ncbi.get_lineage(x) for x in all_orgs]
        names = [ncbi.get_taxid_translator(x) for x in lineages]

        for lineage, name in zip(lineages, names):
            curr_names = []
            for element in lineage[3:]:
                curr_names.append(name[element])
            all_names.append(curr_names)
        return all_names

    @staticmethod
    def _check_organism(all_orgs):
        """
        Check if all organisms could be mapped against the NCBI taxonomy.

        :param column: Array of all organisms
        :type: Numpy ndarray
        """
        if sum(pd.isna(all_orgs)) > 0:
            print(util.OutText.NA_ORG.value)
            sys.exit(0)

        name2taxid = TaxonomyHandler.translate_all(all_orgs)

        if len(name2taxid) != len(all_orgs):
            missing = TaxonomyHandler._find_missing_entries(name2taxid, all_orgs)
            return missing

    @staticmethod
    def translate_all(orgs):
        """
        Returns TaxIDs for all organisms.

        :param orgs: Array of organisms to convert
        :type: Numpy ndarray
        :return: TaxIDs for organism
        :rtype: Dictionary
        """
        ncbi = NCBITaxa()
        name2taxid = ncbi.get_name_translator(orgs)
        return name2taxid

    @staticmethod
    def _check_compounds(column):
        """
        Analyses if all compounds in the guidelines are known.

        :param column: Array of all compounds
        :type: Numpy ndarray
        """
        all_cmps = TaxonomyHandler.get_all_cmps()

        if column.any() not in all_cmps:
            missing_cmps = [x if x not in all_cmps else None for x in column]
            print(util.OutText.M_CMP.value.format(missing_cmps))
        else:
            missing_cmps = []

        return missing_cmps

    @staticmethod
    def get_all_cmps():
        """
        Reads in all known compounds.

        :return: List of all known compounds
        :rtype: List
        """
        cmp_classes = util.read_in_reference_dict('cmp_classes')
        all_cmps = []
        for cmp_class, cmps in cmp_classes.items():
            all_cmps.extend(cmps)
        return all_cmps

    @staticmethod
    def _find_missing_entries(taxids, organisms):
        """
        Returns entries that could not be mapped to the NCBI Taxonomy.

        :param taxids: All converted TaxIDs
        :type: Dictionary
        :param organisms: All organisms that should be converted
        :type: Numpy ndarray
        """
        missing = [x not in taxids.keys() for x in organisms]
        print(util.OutText.M_TAX.value.format(organisms[missing]))
        return organisms[missing]
