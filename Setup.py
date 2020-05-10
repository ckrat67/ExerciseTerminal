from setuptools import setup

setup(
    name='ExerciseTerminal',
    version='0.2',
    py_modules=['ExerciseTerminal'],
    install_requires=[
        'Click',
        'pandas',
        'datetime',

    ],
    entry_points='''
        [console_scripts]
        ex=ExerciseTerminal:log
        initdir=ExerciseTerminal:initialisefiledirectories
        dellog=ExerciseTerminal:deletelog
        modlog=ExerciseTerminal:modifylog
        createex=ExerciseTerminal:createnewexercise
        chknm=ExerciseTerminal:check_exnameexercise
        chkac=ExerciseTerminal:check_acronym
        setdir=ExerciseTerminal:changedefaultdir
        setlogfile=ExerciseTerminal:changeloggingfile
        delex=ExerciseTerminal:deleteexercise
        setreso=ExerciseTerminal:changereso
        querylog=ExerciseTerminal:showlog
        alllogs=ExerciseTerminal:queryalllogs
        sortlog=ExerciseTerminal:sortlogfile
        sortleg=ExerciseTerminal:sortlegend
        ETconfig=ExerciseTerminal:printconfig
        
    ''',
)