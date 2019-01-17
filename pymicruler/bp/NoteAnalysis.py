import re
import codecs
import pandas as pd

from pymicruler.utils import util
from pymicruler.bp.ConsoleClassifier import ConsoleClassifier


class NoteAnalysis:
    def __init__(self):
        self.notes = pd.read_excel(util.Path.IDICT.value)
        self.list_of_patterns = util.NoteRegex.all_patterns.value

        self._read_old_ocurrences()

        self.unknown_note_list = []
        self.int_rules_new = dict()

    def _read_old_ocurrences(self):
        """
        Reads in applicabilities of interpretive rules as analysed in last
        version.
        """
        with open(util.Path.OLD_OCC.value, 'r', encoding='UTF-8') as f_handle:
            self.int_rules_old = eval(f_handle.read())

    def check_if_known(self, entry):
        """
        Analyses if note text was already described in a previous version.

        :param entry: Note text to be analysed.
        :type: String
        """
        if entry not in self.notes.note_text.values:
            self._check_for_pattern(entry)

    def _check_for_pattern(self, entry):
        """
        Analyses if unknown note contains any pattern that mark it as irrelevant.

        :param entry: Unknown note text
        :type: String
        """
        for pattern in self.list_of_patterns:
            if re.search(pattern, entry) is not None:
                self.notes.loc[self.notes.index.max() + 1,
                               ['note_text', 'relevance']] = (entry, 0)
            elif entry not in self.unknown_note_list:
                self.unknown_note_list.append(entry)

    def summarize_note_analysis(self):
        """
        Asks user how to classify unknown comments.
        """
        if len(self.unknown_note_list) == 0:
            return

        choice = input(util.OutText.CHOICE.value.format(
            len(self.unknown_note_list)))
        if choice == 'a':
            ConsoleClassifier.run_console_classification(self.unknown_note_list)
        elif choice == 'b':
            self._save_missing_notes()
        else:
            print(util.OutText.NOANS.value)
            self._save_missing_notes()

    def _save_missing_notes(self):
        """
        Writes out any missing notes for manual classification.
        """
        pd.DataFrame(self.unknown_note_list, columns=['note_text']) \
            .to_excel(util.Path.MISSING_NOTES.value, index=False)

    def get_note_information(self, text, organism, cmp_name):
        """
        Finds all stored information for a specific note.

        :param text: Note text to be analysed
        :type: String
        :param organism: Name of organism the breakpoint is applicable for
        :type: String
        :param cmp_name: Name of compound the breakpoint is applicable for
        :return: Information about content of note
        :rtype: Dictionary
        """
        self.notes = pd.read_excel(util.Path.IDICT.value)
        entry = self.notes[self.notes.note_text == text].iloc[0]
        info_dict = entry.to_dict()

        if info_dict['interpretation'] == 1:
            self._interpretive_rule_logger(text, organism, cmp_name)

        return info_dict

    def _interpretive_rule_logger(self, text, organism, cmp_name):
        """
        Logs applicability of a detected interpretive rule.

        :param text: Note text of rule
        :type: String
        :param organism: Name of organism the breakpoint is applicable for
        :type: String
        :param cmp_name: Name of compound the breakpoint is applicable for
        :type: String
        """
        if text in self.int_rules_new.keys():
            self.int_rules_new[text].append((organism, cmp_name))
        else:
            self.int_rules_new[text] = [(organism, cmp_name)]

    def assess_interpretive_rule_changes(self):
        """
        Compares the application of interpretive rules in the current
        document to the last saved version.
        """
        removed, added, modified = self._compare_notes()
        changes = self._handle_changes(removed, added, modified)
        if len(changes) > 0:
            self._save_interpretive_rule_changes(changes)
            print(util.OutText.INT_CHANGES.value)

    def _handle_changes(self, removed, added, modified):
        """
        Processes any detected changes and summarises them for subsequent output.

        :param removed: all rules that were removed completely with old
        occurrences
        :type: Dictionary
        :param added: all rules that were added with occurrences
        :type: Dictionary
        :param modified: all rules that have changed applicability with occurrences
        :type: Dictionary
        :return: Summary of all changes
        :rtype: List
        """
        changes = []
        if (len(added) + len(removed) + len(modified)) != 0:
            for key in removed:
                changes.append((key, self.int_rules_old[key], 'removed all'))

            for key in added:
                changes.append((key, self.int_rules_new[key], 'added all'))

            for key in modified:
                mod_removed = set(self.int_rules_old[key]) - set(self.int_rules_new[key])
                mod_added = set(self.int_rules_new[key]) - set(self.int_rules_old[key])
                if len(mod_removed) > 0:
                    changes.append((key, list(mod_removed), 'removed'))
                if len(mod_added) > 0:
                    changes.append((key, list(mod_added), 'added'))
        return changes

    def _compare_notes(self):
        """
        Compares interpretive rule occurrences of the last publication to
        occurrences in this publication and saves changes.

        :return: Information about which rules were added, removed and which
        are related to new species, compound combinations.
        :rtype: Set, Set, Dictionary
        """
        d1_keys = set(self.int_rules_old.keys())
        d2_keys = set(self.int_rules_new.keys())

        intersect_keys = d1_keys.intersection(d2_keys)

        removed = d1_keys - d2_keys
        added = d2_keys - d1_keys

        modified = {o: (self.int_rules_old[o],
                        self.int_rules_new[o]) for o in intersect_keys
                    if self.int_rules_old[o] != self.int_rules_new[o]}
        return removed, added, modified

    def _update_comment_reference(self):
        """
        Writes out dictionary with interpretive rule applications to
        be new reference.
        """
        f = codecs.open(util.Path.OLD_OCC.value, 'w', 'UTF-8')
        f.write(str(self.int_rules_new))
        f.close()

    def _save_interpretive_rule_changes(self, changes):
        """
        Saves all added, removed interpretive rules and any changes
        in occurrences.

        :param changes: All differences in the interpretive rule occurrence
        that were found
        :type: List
        """
        df = pd.DataFrame(changes, columns=util.Cols.IRU.value)
        df.to_csv(util.Path.IRU_CHANGES.value, index=False)
        self._update_comment_reference()
