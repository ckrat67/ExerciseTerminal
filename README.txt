Do not alter any file name in this directory - this could cause the application to not work as intended.
Internal data in the text files may be modified as the user pleases.

Description: Lightweight command line program to increase ease of logging and exporting exercise records
Commands supported:

Installation instructions:
    (1) Download Python v3.6+
    (2) Copy ExerciseTerminal.py, Setup.py and CreateRequiredFiles.py to the preferred destination folder.
    (3) After ensuring that your version of Python is set to PATH (run "sysdm.cpl" > Advanced > Environment Variables), call "pip install --editable ." in the folder with the three files.
    (4) Call "initdir" and start using.

COMMANDS:
    (1) initialise directory: initdir
    (2) log exercise:                                   ex -l <time in DDMMYYYY-HHmm or HHmm form>, or just "ex" for logging "now"
    (3) delete log:                                     dellog
    (4) modify log:                                     modlog
    (5) create exercise:                                createex
    (6) delete exercise from legend:                    delex
    (7) check full name of exercise from its acronym:   chknm
    (8) check acronym of exercise from its full name:   chkac
    (9) query slice of log file (and export file):      querylog
    (10) query all logs in log file (and export file):  alllogs (does not work if there are blank lines in the selected log file)
    (11) sort all logs in log file (by date/time):      sortlog
    (12) sort legend (by alphabet):                     sortleg

Manual Tools:
    (1) change config.txt directory:                    setdir
    (2) change config.txt logging file:                 setlogfile
    (3) change config.txt resolution:                   setreso
    (4) print contents of config.txt:                   ETconfig

ABORT process:
    Pressing the "CTRL+C" will abort any running ExerciseTerminal process.