import pandas as pd

from pymicruler.utils import util


class ConsoleClassifier:
    @staticmethod
    def run_console_classification(new_notes):
        """
        Starts workflow to classify new notes directly via the console.

        :param new_notes: All unknown notes
        :type: List
        """
        notes = pd.read_excel(util.Path.IDICT.value, index_col=None)
        for element in new_notes:
            print(element)
            comment_info = {'note_text': element}
            choice = input(util.OutText.REL.value)

            if choice.lower() == 'n':
                comment_info['relevance'] = 0
            elif choice.lower() == 'y':
                comment_info = ConsoleClassifier._analyse_relevant_notes(
                    comment_info)
            else:
                print(util.OutText.YON.value)
                comment_info = ConsoleClassifier._analyse_relevant_notes(
                    comment_info)

            notes = notes.append(comment_info, ignore_index=True, verify_integrity=True)
        notes.to_excel(util.Path.IDICT.value)

    @staticmethod
    def _analyse_relevant_notes(comment_info):
        """
        Asks user for information about the note to best classify the new note.

        :param comment_info: contains all known information about the new note.
        :type: Dictionary
        :return: updated information about the new comment
        :rtype:  Dictionary
        """
        comment_info['relevance'] = 1

        choice = input(util.OutText.GCLASS.value)

        if choice.lower() == 'a':
            comment_info['interpretation'] = 1
        elif choice.lower() == 'b':
            comment_info['resistance'] = 1
        elif choice.lower() == 'c':
            comment_info['roa'] = input(util.OutText.ROA.value)
        elif choice.lower() == 'd':
            comment_info['indication'] = input(util.OutText.IND.value)
        elif choice.lower() == 'e':
            comment_info['exception'] = input(util.OutText.EXC.value)
        elif choice.lower() == 'f':
            comment_info['new_bp'] = input(util.OutText.BP.value)
        elif choice.lower() == 'g':
            comment_info['not_encodable'] = 1
        else:
            print(util.OutText.INV.value)

        if 'interpretation' not in comment_info.keys():
            comment_info['other_information'] = 1

        return comment_info
