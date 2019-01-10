from pyknow import *
from pymicruler.utils import util
from pymicruler.bp.TaxonomyHandler import TaxonomyHandler as TH
import pandas as pd


class Init(Fact):
    pass


class Resistance(Fact):
    pass


class Susceptibility(Fact):
    pass


class Intermediate(Fact):
    pass


class Organism(Fact):
    pass


class MIC(Fact):
    pass


class BetaLactamase(Fact):
    pass


class Mec(Fact):
    pass


class InducibleMlsbResistance(Fact):
    pass


class BacterialResistance(KnowledgeEngine):
    def __init__(self):
        self.out_res = {}
        self.compound_classes = util.read_in_reference_dict('cmp_classes')
        self.phen_dict = util.read_in_reference_dict('phen_groups')
        self.beta_lactam_agents = util.Info.BLA.value
        self.cmp_for_mrsa = ()
        self.isoxazolyl_penicillins = util.Info.ISOXAZYL.value
        self.penicillin_with_inhibitor = util.Info.INH.value
        self.all_families = util.Info.CMP_CLASS.value
        self.all_unclassified = util.Info.UNCLASS.value
        super().__init__()

    def anyof(*what):
        """
        Returns True if a fact matches any of the entries given as argument.

        :param what: alternatives that can be matched
        :type: List
        :return: True/False whether the fact matches any of the entries.
        :rtype: Boolean
        """
        return P(lambda y: y in what)

    def declare_cmp_family(self, compound_class, info_type, exceptions=None):
        """
        Gets all members of a compound family from the database and adds them individually with
        the provdided label.

        :param compound_class: name of the compound class which should be defined.
        :type: String
        :param info_type: Label for resistance phenotype 'R', 'I', or 'S'
        :type: String
        :param exceptions: list of compounds that should not be declared. Default = None
        :type: List
        """
        compound_list = self.compound_classes[compound_class]
        if exceptions is not None:
            compound_list = [x for x in compound_list if x not in exceptions]
        if info_type == 'S':
            for element in compound_list:
                self.declare(Susceptibility(cmp_name=element))
        elif info_type == 'R':
            for element in compound_list:
                self.declare(Resistance(cmp_name=element))
        else:
            for element in compound_list:
                self.declare(Intermediate(cmp_name=element))

    def declare_cmp_list(self, cmp_list, info_type):
        """
        Declares the given resistance label for all compounds in the list.

        :param cmp_list: compounds that should be declared as R, S or I.
        :type: List
        :param info_type: Label for resistance phenotype 'R', 'I', or 'S'.
        :type: String
        """
        if info_type == 'R':
            for cmp in cmp_list:
                self.declare(Resistance(cmp_name=cmp))
        elif info_type == 'S':
            for cmp in cmp_list:
                self.declare(Susceptibility(cmp_name=cmp))
        else:
            for cmp in cmp_list:
                self.declare(Intermediate(cmp_name=cmp))

    def check_if_group_member(self, organism):
        """
        Checks whether the organism that is analysed is member of any phenotypically defined group.

        :param organism: name of the species that is analysed.
        :type: String
        """
        for key, item in self.phen_dict.items():
            if organism in item:
                self.declare(Organism(name=key))

    def process_organism(self, organism):
        """
        Takes the species that should be analysed and declares all taxonomic parents and
        checks whether eny of them is member of a phenotypically defined group.

        :param organism: name of the species
        :type: String
        """
        all_lineages = list()
        all_lineages.append(organism)
        taxid = TH.translate_all(all_lineages)
        lineage = TH.get_all_lineages(taxid[organism])[0]
        for entry in lineage:
            self.declare(Organism(name=entry))
            self.check_if_group_member(entry)

    def _write_out_all_phenotypes(self, cmp, res_dict, label):
        """
        Writes out all new resistance phenotypes if they do not contradict AST results.
        :param cmp: Compound name
        :type: String
        :param res_dict: Dictionary containing the initially known phenotypes
        :type: Dictionary
        :param label: The phenotype that was determined for the compound ('R'/'S'/'I').
        :type: String
        """
        if cmp['cmp_name'] not in res_dict.keys() or res_dict[cmp['cmp_name']]['label'] == '':
            if cmp['cmp_name'] not in self.out_res.keys():
                self.out_res[cmp['cmp_name']] = label
            elif self.out_res[cmp['cmp_name']] != label:
                print(util.OutText.INCOMPATIBLE.value.format(
                    label, self.out_res[cmp['cmp_name']]), res_dict['organism'], cmp['cmp_name'])
        elif res_dict[cmp['cmp_name']]['label'] != label:
            print(util.OutText.DIFFERENT.value.format(
                label, res_dict[cmp['cmp_name']]['label'],
                res_dict['organism'], cmp['cmp_name']))

    @Rule(NOT(Init()))
    def get_initial_info(self):
        print('No information was provided, try again')

    @Rule(Init(res_dict=MATCH.res_dict), salience=2)
    def declare_all_resistance_labels(self, res_dict):
        for key, item in res_dict.items():
            if key == 'organism':
                self.process_organism(item)
                continue
            elif item['label'] == 'R':
                self.declare(Resistance(cmp_name=key))
            elif item['label'] == 'S':
                self.declare(Susceptibility(cmp_name=key))
            elif item['label'] == 'I':
                self.declare(Intermediate(cmp_name=key))
            self.declare(MIC(cmp_name=key, mic=item['mic']))

    @Rule(Init(), salience=3)
    def clear_out_res(self):
        self.out_res = {}

    @Rule(AND(Organism(name='Staphylococcus'),
              OR(Resistance(cmp_name=anyof('Oxacillin', 'Cefoxitin')),
                 Mec(present='True'))))
    def exec_rule_8_1(self):
        for element in self.beta_lactam_agents:
            self.declare_cmp_family(element, info_type='R')
            # exceptions for ab used for treating MRSA missing (self.cmp_for_MRSA)

    @Rule(AND(Organism(name='Staphylococcus'),
              OR(Resistance(cmp_name='Benzylpenicillin'),
                 BetaLactamase(present='True'))))
    def exec_rule_8_2(self):
        exception_list = self.isoxazolyl_penicillins + self.penicillin_with_inhibitor
        exception_list.append('Methicillin')
        self.declare_cmp_family('Penicillins', 'R', exception_list)

    @Rule(AND(Organism(name=anyof('Group A', 'Group B', 'Group C', 'Group G')),
              Susceptibility(cmp_name='Benzylpenicillin')))
    def exec_rule_8_3(self):
            amino_list = 'Amoxicillin', 'Ampicillin'
            self.declare_cmp_family('Cephalosporins', 'S')
            self.declare_cmp_family('Carbapenems', 'S')
            self.declare_cmp_list(amino_list, 'S')

    # 8.4 no info, 8.5. described below as exec_rule_bp_t_vir_group_1-3

    @Rule(AND(Organism(name='Enterococcus'),
              Resistance(cmp_name='Ampicillin')))
    def exec_rule_8_6(self):
        self.declare(Resistance(cmp_name='Piperacillin'))
        self.declare_cmp_family('Carbapenems', info_type='R')
        # not in db
        # self.declare(Resistance(cmp_name='Azlocillin'))
        # self.declare(Resistance(cmp_name='Mezlocillin'))

    # 9.1 and 9.2 only warnings

    @Rule(AND(Organism(name='Enterobacterales'),
              Resistance(cmp_name='Ticarcillin'),
              AS.fct << Susceptibility(cmp_name='Piperacillin')))
    def exec_rule_9_3(self, fct):
        self.retract(fct)
        self.declare(Resistance(cmp_name='Piperacillin'))

    @Rule(AND(Organism(name='Haemophilus influenzae'),
              BetaLactamase(present='True')))
    def exec_rule_10_1(self):
        cmp_list = ('Ampicillin', 'Amoxicillin', 'Piperacillin')
        self.declare_cmp_list(cmp_list, 'R')

    @Rule(AND(Organism(name='Haemophilus influenzae'),
              OR(AND(BetaLactamase(present='False'),
                     Resistance(cmp_name='Ampicillin')),
                 AND(BetaLactamase(present='True'),
                     Resistance(cmp_name='Amoxycillin-clavulanic acid')))))
    def exec_rule_10_2_and_3(self):
        cmp_list = ('Ampicillin', 'Amoxicillin', 'Amoxycillin-clavulanic acid',
                    'Ampicillin-sulbactam', 'Piperacillin', 'Piperacillin-tazobactam', 'Cefaclor',
                    'Cefuroxime', 'Cefuroxime axetil')
        self.declare_cmp_list(cmp_list, 'R')

    @Rule(AND(Organism(name='Neisseria gonorrhoeae'),
              BetaLactamase(present='True')))
    def exec_rule_10_4(self):
        cmp_list = ('Ampicillin', 'Amoxycillin', 'Benzylpenicillin')
        self.declare_cmp_list(cmp_list, 'R')

    @Rule(Resistance(cmp_name='Erythromycin'))
    def exec_rule_11_1_1(self):
        cmp_list = ('Azithromycin', 'Clarithromycin', 'Roxithromycin')
        self.declare_cmp_list(cmp_list, 'R')

    @Rule(Susceptibility(cmp_name='Erythromycin'))
    def exec_rule_11_1_2(self):
        cmp_list = ('Azithromycin', 'Clarithromycin', 'Roxithromycin')
        self.declare_cmp_list(cmp_list, 'S')

    @Rule(Intermediate(cmp_name='Erythromycin'))
    def exec_rule_11_1_3(self):
        cmp_list = ('Azithromycin', 'Clarithromycin', 'Roxithromycin')
        self.declare_cmp_list(cmp_list, 'I')

    @Rule(AND(Organism(name='Staphylococcus'),
              Resistance(cmp_name='Erythromycin'),
              AS.fct << Susceptibility(cmp_name='Clindamycin'),
              InducibleMlsbResistance(present='True')))
    def exec_rule_11_2(self, fct):
        self.retract(fct)
        self.declare(Resistance(cmp_name='Clindamycin'))

    # 11.3 only warning

    @Rule(OR(AND(Organism(name='Peptostreptococcus'),
                 MIC(cmp_name='Erythromycin', mic=MATCH.mic),
                 TEST(lambda mic: mic > 8),
                 AS.fct << Susceptibility(cmp_name='Clindamycin')),
             AND(Organism(name='Bacteroides'),
                 MIC(cmp_name='Erythromycin', mic=MATCH.mic),
                 TEST(lambda mic: mic > 32),
                 AS.fct << Susceptibility(cmp_name='Clindamycin'))))
    def exec_rule_11_4(self, fct):
        self.retract(fct)
        self.declare(Resistance(cmp_name='Clindamycin'))

    @Rule(AND(Organism(name='Staphylococcus'),
              Resistance(cmp_name='Clindamycin')))
    def exec_rule_11_5(self):
        print('Warning: Bactericidal activity of quinupristin–dalfopristin is reduced')

    @Rule(AND(Organism(name='Staphylococcus'),
              MIC(cmp_name='Kanamycin', mic=MATCH.mic),
              TEST(lambda mic: mic > 8)))
    def exec_rule_12_1(self):
        self.declare(Resistance(cmp_name='Amikacin'))

    @Rule(AND(Organism(name='Staphylococcus'),
              Resistance(cmp_name='Tobramycin')))
    def exec_rule_12_2(self):
        self.declare(Resistance(cmp_name='Kanamycin'))
        self.declare(Resistance(cmp_name='Amikacin'))

    @Rule(AND(Organism(name='Staphylococcus'),
              Resistance(cmp_name='Gentamicin')))
    def exec_rule_12_3(self):
        self.declare_cmp_family('Aminoglycosides', 'R')

    @Rule(AND(Organism(name=anyof('Enterococcus', 'Streptococcus')),
              Resistance(cmp_name='Kanamycin')))
    def exec_rule_12_5(self):
        self.declare(Resistance(cmp_name='Amikacin'))
        # high level resistance is not included

    @Rule(AND(Organism(name=anyof('Enterococcus', 'Streptococcus')),
              Resistance(cmp_name='Gentamicin'),
              MIC(cmp_name='Gentamicin', mic=MATCH.mic),
              TEST(lambda mic: mic > 128)))
    def exec_rule_12_6(self):
        exception_list = ['Streptomycin']
        self.declare_cmp_family('Aminoglycosides', exception_list)

    @Rule(AND(Organism(name=anyof('Pseudomonas aeruginosa', 'Acinetobacter baumannii')),
              OR(Resistance(cmp_name='Tobramycin'),
                 Intermediate(cmp_name='Tobramycin')),
              Susceptibility(cmp_name='Gentamicin'),
              AS.fct << Susceptibility(cmp_name='Amikacin')))
    def exec_rule_12_7_1(self, fct):
        self.retract(fct)
        self.declare(Resistance(cmp_name='Amikacin'))

    @Rule(AND(Organism(name='Enterobacterales'),
              OR(Resistance(cmp_name='Tobramycin'),
                 Intermediate(cmp_name='Tobramycin')),
              Susceptibility(cmp_name='Gentamicin'),
              AS.fct << Susceptibility(cmp_name='Amikacin')))
    def exec_rule_12_7_2(self, fct):
        self.retract(fct)
        self.declare(Intermediate(cmp_name='Amikacin'))

    @Rule(AND(Organism(name='Enterobacterales'),
              AS.fct << Intermediate(cmp_name='Gentamicin'),
              Susceptibility(cmp_name=anyof('Amikacin', 'Tobramycin', 'Kanamycin', 'Netilmicin',
                                            'Streptomycin', 'Neomycin')),
              NOT(Resistance(cmp_name=anyof('Amikacin', 'Tobramycin', 'Kanamycin', 'Netilmicin',
                                            'Streptomycin', 'Neomycin')))))
    def exec_rule_12_8(self, fct):
        self.retract(fct)
        self.declare(Resistance(cmp_name='Gentamicin'))

    @Rule(AND(Organism(name='Enterobacterales'),
              AS.fct << Intermediate(cmp_name='Tobramycin'),
              Resistance(cmp_name='Gentamicin'),
              Susceptibility(cmp_name='Amikacin')))
    def exec_rule_12_9(self, fct):
        self.retract(fct)
        self.declare(Resistance(cmp_name='Tobramycin'))

    @Rule(AND(Organism(name='Enterobacterales'),
              AS.fct << Intermediate(cmp_name='Netilmicin'),
              AND(OR(Resistance(cmp_name='Gentamicin'),
                     Intermediate(cmp_name='Gentamicin')),
                  OR(Resistance(cmp_name='Tobramycin'),
                     Intermediate(cmp_name='Tobramycin')))))
    def exec_rule_12_10(self, fct):
        self.retract(fct)
        self.declare(Resistance(cmp_name='Netilmicin'))

    # 13_1 is just a warning

    @Rule(AND(Organism(name=anyof('Staphylococcus', 'Streptococcus pneumoniae')),
              Resistance(cmp_name=anyof('Moxifloxacin', 'Levofloxacin'))))
    def exec_rule_13_2_and_13_4(self):
        self.declare_cmp_family('Fluoroquinolones', 'R')

    # 13.3 is just a warning

    @Rule(AND(Organism(name='Enterobacterales'),
              Resistance(cmp_name='Ciprofloxacin')))
    def exec_rule_13_5(self):
        self.declare_cmp_family('Fluoroquinolones', info_type='R')

    @Rule(AND(Organism(name='Salmonella'),
              MIC(cmp_name='Ciprofloxacin', mic=MATCH.mic),
              TEST(lambda mic: mic > 0.06)))
    def exec_rule_13_6(self):
        self.declare_cmp_family('Fluoroquinolones', 'R')

    @Rule(AND(Organism(name='Neisseria gonorrhoeae'),
              Resistance(cmp_name=anyof('Ciprofloxacin', 'Ofloxacin'))))
    def exec_rule_13_8(self):
        self.declare_cmp_family('Fluoroquinolones', 'R')

# Start of rules derived from breakpoint table

    '''@Rule(Organism(name=anyof('Morganella', 'Proteus', 'Providencia')))
    def exec_rule_bp_t_enterobacterales_carbapenems(self):
        self.declare(Resistance(cmp_name='Imipenem', res_type='low-level'))'''

    @Rule(AND(Organism(name='Staphylococcus'),
              Susceptibility(cmp_name='Benzylpenicillin'),
              Susceptibility(cmp_name='Cefoxitin')))
    def exec_rule_bp_t_staphylococcus_penicillins_1_1(self):
        agents = ('Phenoxymethylpenicillin', 'Ampicillin', 'Amoxicillin', 'Piperacillin',
                  'Ticarcillin')
        self.declare_cmp_list(agents, 'S')

    @Rule(AND(Organism(name='Staphylococcus'),
              Resistance(cmp_name='Benzylpenicillin'),
              Susceptibility(cmp_name='Cefoxitin')))
    def exec_rule_bp_t_staphylococcus_penicillins_1_2(self):
        agents = list(self.penicillin_with_inhibitor + self.isoxazolyl_penicillins)
        agents.append('Nafcillin')
        self.declare_cmp_list(agents, 'S')
        # missing 'many Cephalosporins', maybe included in other rules - need to check

    @Rule(AND(Organism(name='Staphylococcus'),
              Resistance(cmp_name='Cefoxitin')))
    def exec_rule_bp_t_staphylococcus_penicillins_1_3(self):
        for agent in self.beta_lactam_agents:
            if agent == 'Cephalosporins':
                self.declare_cmp_family('Cephalosporins', 'R',
                                        exceptions=('Ceftaroline', 'Ceftobiprole'))
            else:
                self.declare_cmp_family(agent, 'R')

    @Rule(AND(Organism(name='Staphylococcus saprophyticus'),
              Susceptibility(cmp_name='Ampicillin')))
    def exec_rule_bp_t_staphylococcus_penicillins_3(self):
        cmp_list = ('Ampicillin', 'Amoxicillin', 'Amoxycillin-clavulanic acid',
                    'Ampicillin-sulbactam', 'Piperacillin', 'Piperacillin-tazobactam')
        self.declare(Mec(present='False'))
        self.declare_cmp_list(cmp_list, 'S')

    @Rule(AND(Organism(name=anyof('Staphylococcus aureus', 'Staphylococcus lugdunensis',
                                  'Staphylococcus saprophyticus')),
              MIC(cmp_name='Oxacillin', mic=MATCH.mic),
              TEST(lambda mic: mic > 2)))
    def exec_rule_bp_t_staphylococcus_penicillins_4_1(self):
        self.declare(Mec(present='True'))

    @Rule(AND(Organism(name='Coagulase-negative'),
              NOT(Organism(name='Staphylococcus saprophyticus')),
              NOT(Organism(name='Staphylococcus lugdunensis')),
              MIC(cmp_name='Oxacillin', mic=MATCH.mic),
              TEST(lambda mic: mic > 0.25)))
    def exec_rule_bp_t_staphylococcus_penicillins_4_2(self):
        self.declare(Mec(present='True'))

    @Rule(AND(Organism(name='Staphylococcus'),
              Susceptibility(cmp_name='Cefoxitin')))
    def exec_rule_bp_t_staphylococcus_cephalosporin_1_and_carbapenems_1(self):
        ceph_agents = ('Cefaclor', 'Cefadroxil', 'Cefalexin', 'Cefazolin', 'Cefepime', 'Cefotaxime',
                       'Cefpodoxime', 'Ceftriaxone', 'Cefuroxime')
        self.declare_cmp_list(ceph_agents, 'S')
        self.declare_cmp_family('Carbapenems', 'S')

    @Rule(OR(AND(OR(Organism(name='Staphylococcus aureus'),
                 Organism(name='Staphylococcus lugdunensis')),
                 MIC(cmp_name='Cefoxitin', mic=MATCH.mic),
                 TEST(lambda mic: mic > 4)),
             AND(Organism(name='Staphylococcus saprophyticus'),
                 MIC(cmp_name='Cefoxitin', mic=MATCH.mic),
                 TEST(lambda mic: mic > 8))))
    def exec_rule_bp_t_staphylococcus_cephalosporin_3(self):
        self.declare(Mec(present='True'))

    @Rule(AND(Organism(name='Staphylococcus aureus'),
              OR(Mec(present='False'),
                 Susceptibility(cmp_name='Methicillin'))))
    def exec_rule_bp_t_staphylococcus_cephalosporin_5_and_7(self):
        cmp_list = ('Ceftaroline', 'Ceftobiprole')
        self.declare_cmp_list(cmp_list, 'S')

    @Rule(AND(Organism(name=anyof('Group A', 'Group B', 'Group C', 'Group G',
                                  'Staphylococcus aureus', 'Viridans group streptococci')),
              Susceptibility(cmp_name='Vancomycin')))
    def exec_rule_bp_t_staphylococcus_glyco_4(self):
        self.declare(Susceptibility(cmp_name='Dalbavancin'))
        self.declare(Susceptibility(cmp_name='Oritavancin'))

    @Rule(AND(Organism(name='Staphylococcus aureus'),
              Mec(present='True'),
              Susceptibility(cmp_name='Vancomycin')))
    def exec_rule_bp_t_staphylococcus_glyco_5(self):
        self.declare(Susceptibility(cmp_name='Telavancin'))

    @Rule(AND(Organism(name='Staphylococcus aureus'),
              Mec(present='True'),
              MIC(cmp_name='Telavancin', mic=MATCH.mic),
              TEST(lambda mic: mic > 0.125)))
    def exec_rule_bp_t_mrsa_glyco_telavancin(self):
        self.declare(Resistance(cmp_name='Telavancin'))

    @Rule(AND(Organism(name='Staphylococcus aureus'),
              Mec(present='True'),
              MIC(cmp_name='Telavancin', mic=MATCH.mic),
              TEST(lambda mic: mic <= 0.125)))
    def exec_rule_bp_t_staphylococcus_glyco_telavancin(self):
        self.declare(Susceptibility(cmp_name='Telavancin'))

    @Rule(AND(Organism(name=anyof('Group A', 'Group B', 'Group C', 'Group G', 'Staphylococcus',
                                  'Streptococcus pneumoniae', 'Haemophilus influenzae',
                                  'Moraxella catarrhalis')),
              Susceptibility(cmp_name='Tetracycline')))
    def exec_rule_bp_t_staphylococcus_tetracyclines_1(self):
        self.declare(Susceptibility(cmp_name='Doxycycline'))
        self.declare(Susceptibility(cmp_name='Minocycline'))

    @Rule(AND(Organism(name=anyof('Group A', 'Group B', 'Group C', 'Group G', 'Staphylococcus')),
              Susceptibility(cmp_name='Linezolid')))
    def exec_rule_bp_t_staphylococcus_oxazolidinones_1(self):
        self.declare(Susceptibility(cmp_name='Tedizolid'))

    @Rule(AND(Organism(name='Enterococcus faecium'),
              Resistance(cmp_name=anyof('Ampicillin', 'Amoxicillin', 'Piperacillin')),
              NOT(Susceptibility(cmp_name=anyof('Ampicillin', 'Amoxicillin', 'Piperacillin')))))
    def exec_rule_bp_t_enterococcus_penicillins_1_2(self):
        for element in self.beta_lactam_agents:
            self.declare_cmp_family(element, 'R')

    @Rule(AND(Organism(name='Enterococcus'),
              Susceptibility(cmp_name='Ampicillin')))
    def exec_rule_bp_t_enterococcus_penicillins_1_3(self):
        cmp_list = ('Amoxicillin', 'Piperacillin', 'Amoxicillin-clavulanic acid',
                    'Piperacillin-tazobactam', 'Ampicillin-sulbactam')
        self.declare_cmp_list(cmp_list, 'S')

    @Rule(AND(Organism(name=anyof('Enterococcus', 'Viridans group streptococci')),
              MIC(cmp_name='Gentamicin', mic=MATCH.mic),
              TEST(lambda mic: mic > 128)))
    def exec_rule_bp_t_enterococcus_aminoglycosides_2_1(self):
        exceptions = ['Streptomycin']
        self.declare_cmp_family('Aminoglycosides', 'R', exceptions)
        # Maybe add low level resistance to Gentamicin in case mic is below 128

    @Rule(AND(Organism(name=anyof('Enterococcus', 'Viridans group streptococci')),
              MIC(cmp_name='Gentamicin', mic=MATCH.mic),
              TEST(lambda mic: mic <= 128)))
    def exec_rule_bp_t_enterococcus_aminoglycosides_2_2(self):
        self.declare(Resistance(cmp_name='Gentamicin', res_type='low-level'))

    @Rule(AND(Organism(name='Enterococcus'),
              MIC(cmp_name='Streptomycin', mic=MATCH.mic),
              TEST(lambda mic: mic > 512)))
    def exec_rule_bp_t_enterococcus_aminoglycosides_3_1(self):
        self.declare(Resistance(cmp_name='Streptomycin'))

    @Rule(AND(Organism(name='Enterococcus'),
              MIC(cmp_name='Streptomycin', mic=MATCH.mic),
              TEST(lambda mic: mic > 512)))
    def exec_rule_bp_t_enterococcus_aminoglycosides_3_2(self):
        self.declare(Resistance(cmp_name='Streptomycin', type='low-level'))

    @Rule(AND(Organism(name=anyof('Group A', 'Group C', 'Group G')),
              Susceptibility(cmp_name='Benzylpenicillin')))
    def exec_rule_bp_t_streptococcus_penicillins_1_1(self):
        exceptions = ('Ticarcillin', 'Ticarcillin-clavulanic acid', 'Temocillin', 'Mecillinam',
                      'Methicillin')
        self.declare_cmp_family('Penicillins', 'S', exceptions)

    @Rule(AND(Organism(name='Group B'),
              Susceptibility(cmp_name='Benzylpenicillin')))
    def exec_rule_bp_t_streptococcus_penicillins_1_2(self):
        exceptions = list('Phenoxymethylpenicillin') + self.isoxazolyl_penicillins
        exceptions.append('Methicillin')
        self.declare_cmp_family('Penicillins', exceptions=exceptions, info_type='S')

    @Rule(AND(Organism(name='Streptococus pneumoniae'),
              Susceptibility(cmp_name='Benzylpenicillin')))
    def exec_rule_bp_t_s_pneumoniae_penicillin_1(self):
        exceptions = ['Ticarcillin', 'Ticarcillin-clavulanic acid', 'Temocillin', 'Mecillinam',
                      'Methicillin'] + \
                     self.isoxazolyl_penicillins
        ceph_list = ('Cefaclor', 'Cefepime', 'Cefotaxime', 'Cefpodoxime', 'Ceftaroline',
                     'Ceftobiprole', 'Ceftriaxone', 'Cefuroxime')
        self.declare_cmp_family('Penicillins', exceptions=exceptions, info_type='S')
        self.declare_cmp_family('Carbapenems', info_type='S')
        self.declare_cmp_list(ceph_list, 'S')

    @Rule(AND(Organism(name='Streptococus pneumoniae'),
              Susceptibility(cmp_name='Ampicillin')))
    def exec_rule_bp_t_s_pneumoniae_penicillin_4(self):
        cmp_list = ('Piperacillin', 'Piperacillin-tazobactam', 'Amoxycillin',
                    'Amoxycillin-clavulanic acid', 'Ampicillin-sulbactam')
        self.declare_cmp_list(cmp_list, 'S')

    @Rule(AND(Organism(name='Viridans group streptococci'),
              Resistance(cmp_name='Benzylpenicillin'),
              Resistance(cmp_name='Ampicillin')))
    def exec_rule_bp_t_vir_group_1_1(self):
        cmp_list = ('Piperacillin', 'Piperacillin-tazobactam',
                    'Amoxycillin-clavulanic acid', 'Ampicillin-sulbactam')
        self.declare_cmp_list(cmp_list, 'R')

    @Rule(AND(Organism(name='Viridans group streptococci'),
              Resistance(cmp_name='Benzylpenicillin'),
              Susceptibility(cmp_name='Ampicillin')))
    def exec_rule_bp_t_vir_group_1_2(self):
        cmp_list = ('Piperacillin', 'Piperacillin-tazobactam',
                    'Amoxycillin-clavulanic acid', 'Ampicillin-sulbactam')
        self.declare_cmp_list(cmp_list, 'S')

    @Rule(AND(Organism(name='Viridans group streptococci'),
              Susceptibility(cmp_name='Benzylpenicillin')))
    def exec_rule_bp_t_vir_group_1_3(self):
        cmp_list = ('Piperacillin', 'Piperacillin-tazobactam',
                    'Amoxycillin-clavulanic acid', 'Ampicillin-sulbactam')
        self.declare_cmp_list(cmp_list, 'S')

    @Rule(AND(Organism(name='Haemophilus influenzae'),
              OR(BetaLactamase(present='True'))))
    def exec_rule_bp_t_h_influenzae_penicillin_2(self):
        cmp_list = ('Ampicillin', 'Amoxicillin', 'Piperacillin')
        self.declare_cmp_list(cmp_list, 'R')

    @Rule(AND(Organism(name=anyof('Haemophilus influenzae', 'Moraxella catarrhalis')),
              Susceptibility(cmp_name='Amoxycillin-clavulanic acid')))
    def exec_rule_bp_t_h_influenzae_penicillin_4(self):
        self.declare(Susceptibility(cmp_name='Ampicillin-sulbactam'))
        self.declare(Susceptibility(cmp_name='Piperacillin-tazobactam'))

    @Rule(AND(Organism(name='Haemophilus influenzae'),
              Susceptibility(cmp_name=anyof('Amoxycillin', 'Ampicillin'))))
    def exec_rule_bp_t_h_influenzae_penicillin_6(self):
        self.declare(Susceptibility(cmp_name='Piperacillin'))

    @Rule(AND(Organism(name='Moraxella catarrhalis'),
              BetaLactamase(present='True')))
    def exec_rule_bp_t_m_catarrhalis_penicillin_1(self):
        cmp_list = ('Ampicillin', 'Amoxicillin', 'Piperacillin', 'Benzylpenicillin',
                    'Phenoxymethylpenicillin')
        self.declare_cmp_list(cmp_list, 'R')

    @Rule(AND(Organism(name='Moraxella catarrhalis'),
              Susceptibility('Amoxycillin-clavulanic acid')))
    def exec_rule_bp_t_m_catarrhalis_penicillin_3(self):
        self.declare(Susceptibility(cmp_name='Ampicillin-sulbactam'))
        self.declare(Susceptibility(cmp_name='Piperacillin-tazobactam'))

    @Rule(AND(Organism(name='Neisseria gonorrhoeae'),
              BetaLactamase(present='False'),
              Susceptibility(cmp_name='Benzylpenicillin')))
    def exec_rule_bp_t_n_gonorrhoeae_penicillin_1(self):
        self.declare(Susceptibility(cmp_name='Ampicillin'))
        self.declare(Susceptibility(cmp_name='Amoxicillin'))

    @Rule(AND(Organism(name=anyof('Gram-positive anaerobes', 'Gram-negative anaerobes')),
              Susceptibility(cmp_name='Benzylpenicillin')))
    def exec_rule_bp_t_gram_pos_anaerobes_penicillin_1(self):
        cmp_list = ('Ampicillin', 'Amoxicillin', 'Piperacillin', 'Ticarcillin')
        self.declare_cmp_list(cmp_list, 'S')

    @Rule(AND(Organism(name=anyof('Campylobacter jejuni', 'Campylobacter coli', 'Kingella kingae')),
              Susceptibility(cmp_name='Tetracycline')))
    def exec_rule_bp_t_c_jejuni_coli_tetracyclines_1(self):
        self.declare(Susceptibility(cmp_name='Doxycycline'))

    @Rule(AND(Organism(name=anyof('Aerococcus urinae', 'Aerococcus sanguinicola')),
              Susceptibility(cmp_name='Ampicillin')))
    def exec_rule_bp_t_a_sanguinicola_urinae_penicillin_1(self):
        self.declare(Susceptibility(cmp_name='Amoxicillin'))

    @Rule(AND(Organism(name=anyof('Aerococcus urinae', 'Aerococcus sanguinicola')),
              Susceptibility(cmp_name='Ciprofloxacin')))
    def exec_rule_bp_t_a_sanguinicola_urinae_fluoroquinolones_1(self):
        self.declare(Susceptibility(cmp_name='Levofloxacin'))

    @Rule(AND(Organism(name='Kingella kingae'),
              BetaLactamase(present='True')))
    def exec_rule_bp_t_k_kingae_penicillin_1(self):
        cmp_list = ('Benzylpenicillin', 'Ampicillin', 'Amoxicillin')
        self.declare_cmp_list(cmp_list, 'R')

    @Rule(AND(Organism(name='Kingella kingae'),
              Susceptibility(cmp_name='Benzylpenicillin')))
    def exec_rule_bp_t_k_kingae_penicillin_2(self):
        cmp_list = ('Ampicillin', 'Amoxicillin')
        self.declare_cmp_list(cmp_list, 'S')

    @Rule('cmp' << Resistance(),
          Init(res_dict=MATCH.res_dict))
    def print_all_res_cmps(self, cmp, res_dict):
        self._write_out_all_phenotypes(cmp, res_dict, 'R')

    @Rule('cmp' << Susceptibility(),
          Init(res_dict=MATCH.res_dict))
    def print_all_sus_cmps(self, cmp, res_dict):
        self._write_out_all_phenotypes(cmp, res_dict, 'S')

    @Rule('cmp' << Intermediate(),
          Init(res_dict=MATCH.res_dict))
    def print_all_int_cmps(self, cmp, res_dict):
        self._write_out_all_phenotypes(cmp, res_dict, 'I')


def run_rbe(groups):
    """
    Prepares data and starts rule based engine.

    :param groups: AST results grouped by sample_id
    :type: Pandas Groupby
    :return: New resistance information deducted from the rule based engine
    :rtype: Dictionary
    """
    bpe = BacterialResistance()
    results = []
    all_dicts = prepare_data(groups)

    for group_ab in all_dicts:
        bpe.reset()
        bpe.declare(Init(res_dict=group_ab))
        bpe.run()
        results.append(bpe.out_res)

    return results


def prepare_data(groups):
    """
    Transcribes data for each tested sample into a dictionaries for the rule based engine.

    :param groups: AST results grouped by sample_id
    :type: Pandas Groupby
    :return: Resistance information for rule based engine input
    :rtype: List of Dictionaries
    """
    all_dicts = []
    for idx, group in groups:
        res_dict = {'organism': group.organism.iloc[0]}
        for g_idx, row in group.iterrows():
            if pd.notna(row.label):
                res_dict[row.cmp_name] = {'label': row.label, 'mic': row.MIC}
            else:
                res_dict[row.cmp_name] = {'label': '', 'mic': row.MIC}
        all_dicts.append(res_dict)
    return all_dicts
