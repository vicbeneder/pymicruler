.. _preprocessing:

Preprocessing
=============

Run visual basic macro
^^^^^^^^^^^^^^^^^^^^^^^^

1. Create a new macro with the name 'PreProcessExcel' in the respective Eucast Excel file.
2. Copy the following text to the vba editor:

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


3. Run the macro.

The new file will be called 'preprocessed_<name of the original file>' and is saved in the same folder as the preprocessed document.


Remove strikethrough text
^^^^^^^^^^^^^^^^^^^^^^^^^^
Currently there is no automated removal for strikethrough text available. The user is asked to remove any text in the
preprocessed breakpoint table manually before parsing the data.
