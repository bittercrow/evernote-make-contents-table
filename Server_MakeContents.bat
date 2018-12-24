@echo off
call %CD%\Scripts\activate.bat 
cmd /k python %CD%\Evernote_MakeContents_Project\empj\makecontents\Server.py

