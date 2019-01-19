.. _preprocessing:

Pre-processing
===============

Breakpoint Table encoding
^^^^^^^^^^^^^^^^^^^^^^^^^^
A visual basic macro is provided to encode text formatting in a machine readable way, e.g. superscript.

1. Create a new macro with the name 'PreProcessExcel' in the respective EUCAST Excel file.
2. Copy the following text to the vba editor and execute.

Visual Basic Script:
::
    Sub PreProcessExcel()
        Dim Source As Workbook
        Dim Target As Workbook
        Dim currentSheet As Worksheet
        Dim path As String
        Dim out_file As String
        Dim sheetIndex As Integer
        Dim ws As Worksheet
        sheetIndex = 1
        Application.ScreenUpdating = False
        Application.DisplayAlerts = False

        path = ActiveWorkbook.path
        out_file = "preprocessed_" & Left(ActiveWorkbook.Name, InStr(ActiveWorkbook.Name, ".xls") - 1) & ".xlsx"

        Set Source = ActiveWorkbook
        Set Target = Workbooks.Add
        For Each currentSheet In Source.Worksheets
            Set ws = Target.Sheets.Add(After:=Target.Sheets(Target.Sheets.Count))
            ws.Name = currentSheet.Name
            currentSheet.Activate
            currentSheet.Cells.Select
            Selection.Copy
            ws.Activate
            ws.Cells.Select
            ws.Paste
            sheetIndex = sheetIndex + 1

            Dim c As Range
            For Each c In ActiveSheet.UsedRange
                If Len(c) <> 0 Then
                    i = Len(c)
                    If c.Characters(i).Font.Superscript Then
                        While c.Characters(i).Font.Superscript
                            i = i - 1
                        Wend
                        c = Left(c, i) & "§" & Right(c, Len(c) - i)
                    End If
                End If
            Next c

        Next currentSheet
        Target.SaveAs Filename:=path & "/" & out_file
        Application.ScreenUpdating = True
    End Sub

The new file will be called *'preprocessed_<name of the original file>'* and is saved in the same folder as the preprocessed document.


Removing obsolete entries
^^^^^^^^^^^^^^^^^^^^^^^^^^
Obsolete entries are currently encoded as strikethrough text. To exclude these entries the user has to remove this text from the pre-processed EUCAST Breakpoint Tables manually.


