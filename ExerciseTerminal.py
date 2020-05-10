import os
import datetime as dt
import pandas as pd
import CreateRequiredFiles
import click
import getpass
import re
import warnings


warnings.simplefilter(action='ignore', category=FutureWarning)


@click.command()
@click.option('-l', '--log-time', default='now', help= 'Log at specified time: '
                                         '(1) "now" - time of logging set to time command received. '
                                         '(2) "ddmmyyyy-HHMM" - time of logging set to specified time. '
                                         '(3) HHMM - time of logging set to specified time with date set to today. ', required=True, type=str)
@click.option('-e', '--exercise', prompt='Specify exercise in acronym form',  help='Type the ACRONYM for the exercise done; find acronym specified in legends.txt.')
@click.option('-r', '--reps',  prompt='Specify reps', help='Specify reps.')
@click.option('-w', '--weight', prompt='Specify weight (in kilos)',
              help='If no weight specification, type NA or 0.')
@click.option('-d', '--duration',  prompt='Specify duration (seconds - s, mins - m, hours - h)',
              help='If no duration specification, type NA or 0.')
@click.option('-db', '--doneby', prompt='Exercise done by', help='Specify the person doing the exercise. As far as '
                                                                 'possible, keep the name consistent and exact across '
                                                                 'logs. ')
@click.option('-n', '--notes', prompt='Additional notes', default='NA',
              help='Type additional notes; eg, name of the person doing the exercise, if the file is not named after'
                   ' the performer of the exercises.')
def log(log_time, exercise, reps, weight, duration, doneby, notes):
    try:
        dirname = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()[2].strip('\n').split('=')[1]
        logfilename = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()[1].strip('\n').split('=')[1]
    except FileNotFoundError as ex:
        raise Exception(f'Error: {str(ex)}; call "initdir" to initialise directories first. ')

    username = getpass.getuser()
    click.echo('User {} creating log...'.format(username))
    timenow = dt.datetime.now().strftime("%d%m%Y-%H%M")
    click.echo('Logging command received at {}'.format(timenow))

    # check if '_' key is used --> prevent this from being included in log
    if '_' in (log_time, exercise, reps, weight, duration, doneby, notes):
        raise Exception('Error: cannot use "_" character in log. Please try again. ')
    else:
        pass

    dividerstart = '[START]'
    dividerend = '[END]\n'
    ddmmyyyy_HHMM = re.compile('^\d{8}-\d{4}$')
    HHMM = re.compile('^\d{4}$')

    # rewrite config file - directory&logfile
    configupdate = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()
    configupdate[1] = f'Logging_to_File={logfilename}\n'
    configupdate[2] = f'Default_Directory={dirname}\n'
    configupdatex = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'w+')
    configupdatex.writelines(configupdate)
    configupdatex.close()

    # parse log command
    if log_time == "now":
        time = timenow
    elif ddmmyyyy_HHMM.match(log_time):
        timeerror = re.search('^(\d\d)(\d\d)(\d{4})[-](\d\d)(\d\d)$', log_time)
        if int(timeerror.group(1)) <= 0 or int(timeerror.group(1)) > 31 or int(timeerror.group(2)) <= 0 or int(
                timeerror.group(2)) > 12 or int(timeerror.group(3)) > dt.datetime.now().year or int(
                timeerror.group(4)) <= 0 or int(timeerror.group(4)) > 23 or int(timeerror.group(5)) < 0 or int(
                timeerror.group(5)) > 59:
            raise Exception('Error: incorrect date given. Please check date and try again. ')
        else:
            time = log_time
    elif HHMM.match(log_time):
        timeerror = re.search('^(\d\d)(\d\d)$', log_time)
        if int(timeerror.group(1)) > 23 or int(timeerror.group(2)) > 59:
            raise Exception('Error: incorrect date given. Please check date and try again. ')
        else:
            time = f'{timenow.split("-")[0]}-{log_time}'
    else:
        raise Exception('log time specified was not in the correct format. Specify time as either \n'
                        '(1) "now" - time of logging set to time command received. \n'
                        '(2) "ddmmyyyy-HHMM" - time of logging set to specified time. \n'
                        '(3) HHMM - time of logging set to specified time with date set to today.')


    findexercise = re.compile(f'^{exercise}$')
    legend = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'r').readlines()
    for i in legend:
        if findexercise.match(i.split(':')[1].strip('\n')):
            selectedexercise: str = i.split(':')[0]
        else:
            pass
    try:
        selectedexercise # error used to show exercise notfound
    except UnboundLocalError:
        exercisenotfound = input('Error: acronym does not match any exercise compiled in "legend.txt". '
                                 f'Do you want to create a new exercise (acronym "{exercise}"? [y/N]:  ')
        if exercisenotfound == 'y':
            newexercisename = input('What is the name of the exercise to be added to legend.txt? ')
            newacronym = exercise
            selectedexercise = CreateRequiredFiles.createnewexercise_nodecorator(newexercisename, newacronym)
            # createnewexercise()
        else:
            return

    logcreation = f'{dividerstart}' \
                  f'Time:{time}_' \
                  f'Exercise:{selectedexercise}_' \
                  f'Repetitions/Weight/Duration:{reps}/{weight}/{duration}_' \
                  f'DoneBy:{doneby}_' \
                  f'AdditionalNotes:{notes}_' \
                  f'CreatedByComputer:{username}' \
                  f'{dividerend}'
    try:
        logging = open(os.path.join(dirname, "MainLogFiles", f"{logfilename}.txt"), 'a')
        logging.write(logcreation)
        logging.close()
        click.echo(f"logging successful: \n\n{logcreation}")
    except FileNotFoundError as ex:
        print(f'Error, file not found; try calling the "initdir" function first: {str(ex)}')
    except NameError as ex:
        print(f'Error, directory name not found; try calling the "initdir" function first: {str(ex)}')


@click.command()
@click.argument('modify', default=1)
def deletelog(modify):
    if modify == 1:
        logfile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                       'r').readlines()[1].strip('\n').split('=')[1]
        prompt = input(f'Are you sure you want to modify the selected log file "{logfile}.txt"? [y/N]: ')
        if prompt == 'y':
            log = open(os.path.join(
                open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                     'r').readlines()[2].strip('\n').split('=')[1], "MainLogFiles", f"{logfile}.txt"), 'r').readlines()
            modifydatetime = input('Input date and time of the log to delete (format "ddmmyyyy-HHMM") or '
                                   'input "prev" to delete previously made log: ')
            if modifydatetime == 'prev':
                try:
                    prompt2 = input(f"Delete following log? \n{log[-1]}\n [y/N]: ")
                    if prompt2 == 'y':
                        log = log[:-1]
                        overwrite = open(os.path.join(open(os.path.join(os.path.dirname(
                            os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()[2].strip('\n').split(
                            '=')[1], "MainLogFiles", f"{logfile}.txt"), 'w+')
                        overwrite.writelines(log)
                        overwrite.close()
                        print('Log deleted. check file now.')
                    else:
                        print('Aborted process!')
                except IndexError as ex:
                    print(f'Error: log file empty. IndexError raised: {str(ex)} ')
            else:
                # check if queried time input is valid --> raise exception for invalid input!
                timeerror = re.search('^(\d\d)(\d\d)(\d{4})[-](\d\d)(\d\d)$', modifydatetime)
                if int(timeerror.group(1)) <= 0 or int(timeerror.group(1)) > 31 or int(timeerror.group(2)) <= 0 or int(
                        timeerror.group(2)) > 12 or int(timeerror.group(3)) > dt.datetime.now().year or int(
                    timeerror.group(4)) <= 0 or int(timeerror.group(4)) > 23 or int(timeerror.group(5)) < 0 or int(
                    timeerror.group(5)) > 59:
                    raise Exception('Error: incorrect date given. Please check date and try again. ')
                else:
                    pass
                placeholder = 'placeholder'
                for i in range(len(log)):
                    if modifydatetime == log[i].split('_')[0].split(':')[1]:
                        placeholder = i
                    else:
                        pass
                if placeholder == 'placeholder':
                    print('No log found. Please try again. ')
                    return
                else:
                    prompt3 = input(f"Delete following log? \n{log[placeholder]}\n [y/N]: ")
                    if prompt3 == 'y':
                        log.pop(placeholder)
                        overwrite = open(os.path.join(
                            open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles',
                                              "config.txt"),
                                 'r').readlines()[2].strip('\n').split('=')[1], "MainLogFiles", f"{logfile}.txt"), 'w+')
                        overwrite.writelines(log)
                        overwrite.close()
                        print('Log deleted. check file now.')
                    else:
                        print('Aborted process!')
        else:
            print('Aborted process!')
    else:
        raise Exception('Error: function called with incorrect arguments. Please try again. ')


@click.command()
@click.argument('mod', default=1)
def modifylog(mod):
    if mod == 1:
        logfile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                       'r').readlines()[1].strip('\n').split('=')[1]

        log = open(os.path.join(
            open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                 'r').readlines()[2].strip('\n').split('=')[1], "MainLogFiles", f"{logfile}.txt"), 'r').readlines()
        modifydatetime = input('Input date and time of the log to modify (format "ddmmyyyy-HHMM") or '
                               'input "prev" to modify previously made log: ')
        if modifydatetime == 'prev':
            try:
                if click.confirm(f'Do you want to Modify following log? \n\n{log[-1]}\n', abort=True):
                    # split log up into constituents
                    h, ii, j, k, l, m = log[-1].split('_')
                    time = h.split(':')[1]
                    exercise = ii.split(':')[1]
                    repetitions = j.split(':')[1].split('/')[0]
                    weight = j.split(':')[1].split('/')[1]
                    duration = j.split(':')[1].split('/')[2]
                    doneby = k.split(':')[1]
                    additionalnotes = l.split(':')[1]
                    createdbycomputer = re.search('(.*)[[]\w{3}[]]', m.split(':')[1]).group(1)

                    dividerstart = '[START]'
                    dividerend = '[END]\n'

                    timeM = click.prompt('Please enter a valid date/time (format ddmmyyyy-HHMM)', type=str, default=time)
                    timeerror = re.search('^(\d\d)(\d\d)(\d{4})[-](\d\d)(\d\d)$', timeM)
                    try:
                        if int(timeerror.group(1)) <= 0 or int(timeerror.group(1)) > 31 or int(
                                timeerror.group(2)) <= 0 or int(
                                timeerror.group(2)) > 12 or int(timeerror.group(3)) > dt.datetime.now().year or int(
                                timeerror.group(4)) <= 0 or int(timeerror.group(4)) > 23 or int(
                                timeerror.group(5)) < 0 or int(
                                timeerror.group(5)) > 59:
                            raise Exception('Error: incorrect date given. Please check date and try again. ')
                    except AttributeError:
                        raise Exception(f'Error: invalid date format. Please check date input and try again. ')

                    # find exercise acronym
                    legend = open(
                        os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"),
                        'r').readlines()
                    acronym = 0
                    regexname = re.compile(f'^{exercise}$')
                    for i in legend:
                        if regexname.match(i.split(':')[0]):
                            acronym = i.split(":")[1].strip("\n")
                        else:
                            pass
                    if acronym == 0:
                        raise Exception('Error in logs: exercise is not mapped to any acronym. \n'
                                        'Please check legend and manually correct the log file. ')
                    exerciseM = click.prompt(f'Exercise name "{exercise}" has acronym "{acronym}". \nPlease enter exercise acronym', type=str, default=acronym)
                    findexercise = re.compile(f'^{exerciseM}$')
                    legend = open(
                        os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"),
                        'r').readlines()
                    for i in legend:
                        if findexercise.match(i.split(':')[1].strip('\n')):
                            selectedexercise: str = i.split(':')[0]
                        else:
                            pass
                    try:
                        selectedexercise  # error used to show exercise notfound
                    except UnboundLocalError:
                        exercisenotfound = input(
                            'Error: acronym does not match any exercise compiled in "legend.txt". '
                            f'Do you want to create a new exercise (acronym "{exercise}"? [y/N]:  ')
                        if exercisenotfound == 'y':
                            newexercisename = input('What is the name of the exercise to be added to legend.txt? ')
                            newacronym = exercise
                            selectedexercise = CreateRequiredFiles.createnewexercise_nodecorator(newexercisename,
                                                                                                 newacronym)
                        else:
                            return

                    repetitionsM = click.prompt('Please enter no. of repetitions', type=int, default=repetitions)
                    weightM = click.prompt('Please enter weight used', type=str, default=weight)
                    durationM = click.prompt('Please enter duration of exercise', type=str, default=duration)
                    donebyM = click.prompt('Who was the exercise done by', type=str, default=doneby)
                    additionalnotesM = click.prompt('Any additional notes', type=str, default=additionalnotes)
                    createdbycomputerM = click.prompt('Created by computer', type=str, default=createdbycomputer)

                    if '_' in (timeM, selectedexercise, repetitionsM, weightM, durationM, donebyM, additionalnotesM, createdbycomputerM):
                        raise Exception('Error: cannot use "_" character in log. Please try again. ')
                    else:
                        pass

                    logcreation = f'{dividerstart}' \
                                  f'Time:{timeM}_' \
                                  f'Exercise:{selectedexercise}_' \
                                  f'Repetitions/Weight/Duration:{repetitionsM}/{weightM}/{durationM}_' \
                                  f'DoneBy:{donebyM}_' \
                                  f'AdditionalNotes:{additionalnotesM}_' \
                                  f'CreatedByComputer:{createdbycomputerM}' \
                                  f'{dividerend}'

                    log[-1] = logcreation
                    overwrite = open(os.path.join(open(os.path.join(os.path.dirname(
                        os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()[2].strip(
                        '\n').split('=')[1], "MainLogFiles", f"{logfile}.txt"), 'w+')
                    overwrite.writelines(log)
                    overwrite.close()
                    print(f'log modified: \n\n{logcreation}\n')
            except IndexError as ex:
                print(f'Error: log file empty. IndexError raised: {str(ex)} ')

        else:
            # check if queried time input is valid --> raise exception for invalid input!
            timeerror = re.search('^(\d\d)(\d\d)(\d{4})[-](\d\d)(\d\d)$', modifydatetime)
            try:
                if int(timeerror.group(1)) <= 0 or int(timeerror.group(1)) > 31 or int(timeerror.group(2)) <= 0 or int(
                        timeerror.group(2)) > 12 or int(timeerror.group(3)) > dt.datetime.now().year or int(
                        timeerror.group(4)) <= 0 or int(timeerror.group(4)) > 23 or int(timeerror.group(5)) < 0 or int(
                        timeerror.group(5)) > 59:
                    raise Exception('Error: invalid date format. Please check date input and try again. ')
            except AttributeError:
                raise Exception('Error: invalid date format. Please check date input and try again. ')

            placeholder = 'placeholder'
            for i in range(len(log)):
                if modifydatetime == log[i].split('_')[0].split(':')[1]:
                    placeholder = i
                else:
                    pass
            if placeholder == 'placeholder':
                print('No log found. Please try again. ')
                return
            else:
                if click.confirm(f'Do you want to Modify following log? \n\n{log[placeholder]}\n', abort=True):
                    h, ii, j, k, l, m = log[placeholder].split('_')
                    time = h.split(':')[1]
                    exercise = ii.split(':')[1]
                    repetitions = j.split(':')[1].split('/')[0]
                    weight = j.split(':')[1].split('/')[1]
                    duration = j.split(':')[1].split('/')[2]
                    doneby = k.split(':')[1]
                    additionalnotes = l.split(':')[1]
                    createdbycomputer = re.search('(.*)[[]\w{3}[]]', m.split(':')[1]).group(1)

                    dividerstart = '[START]'
                    dividerend = '[END]\n'

                    timeM = click.prompt('Please enter a valid date/time (format ddmmyyyy-HHMM)', type=str, default=time)
                    timeerror = re.search('^(\d\d)(\d\d)(\d{4})[-](\d\d)(\d\d)$', timeM)
                    try:
                        if int(timeerror.group(1)) <= 0 or int(timeerror.group(1)) > 31 or int(
                                timeerror.group(2)) <= 0 or int(
                                timeerror.group(2)) > 12 or int(timeerror.group(3)) > dt.datetime.now().year or int(
                                timeerror.group(4)) <= 0 or int(timeerror.group(4)) > 23 or int(
                                timeerror.group(5)) < 0 or int(
                                timeerror.group(5)) > 59:
                            raise Exception('Error: invalid date format. Please check date input and try again. ')
                    except AttributeError:
                        raise Exception('Error: invalid date format. Please check date input and try again. ')

                    # find exercise acronym
                    legend = open(
                        os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"),
                        'r').readlines()
                    acronym = 0
                    regexname = re.compile(f'^{exercise}$')
                    for i in legend:
                        if regexname.match(i.split(':')[0]):
                            acronym = i.split(":")[1].strip("\n")
                        else:
                            pass
                    if acronym == 0:
                        raise Exception('Error in logs: exercise is not mapped to any acronym. \n'
                                        'Please check legend and manually correct the log file. ')
                    exerciseM = click.prompt(f'Exercise name "{exercise}" has acronym "{acronym}". \nPlease enter exercise acronym', type=str, default=acronym)
                    findexercise = re.compile(f'^{exerciseM}$')
                    legend = open(
                        os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"),
                        'r').readlines()
                    for i in legend:
                        if findexercise.match(i.split(':')[1].strip('\n')):
                            selectedexercise: str = i.split(':')[0]
                        else:
                            pass
                    try:
                        selectedexercise  # error used to show exercise notfound
                    except UnboundLocalError:
                        exercisenotfound = input(
                            'Error: acronym does not match any exercise compiled in "legend.txt". '
                            f'Do you want to create a new exercise (acronym "{exercise}"? [y/N]:  ')
                        if exercisenotfound == 'y':
                            newexercisename = input('What is the name of the exercise to be added to legend.txt? ')
                            newacronym = exercise
                            selectedexercise = CreateRequiredFiles.createnewexercise_nodecorator(newexercisename,
                                                                                                 newacronym)
                        else:
                            return

                    repetitionsM = click.prompt('Please enter no. of repetitions', type=int, default=repetitions)
                    weightM = click.prompt('Please enter weight used', type=str, default=weight)
                    durationM = click.prompt('Please enter duration of exercise', type=str, default=duration)
                    donebyM = click.prompt('Who was the exercise done by', type=str, default=doneby)
                    additionalnotesM = click.prompt('Any additional notes', type=str, default=additionalnotes)
                    createdbycomputerM = click.prompt('Created by computer', type=str, default=createdbycomputer)

                    if '_' in (timeM, selectedexercise, repetitionsM, weightM, durationM, donebyM, additionalnotesM, createdbycomputerM):
                        raise Exception('Error: cannot use "_" character in log. Please try again. ')
                    else:
                        pass

                    logcreation = f'{dividerstart}' \
                                  f'Time:{timeM}_' \
                                  f'Exercise:{selectedexercise}_' \
                                  f'Repetitions/Weight/Duration:{repetitionsM}/{weightM}/{durationM}_' \
                                  f'DoneBy:{donebyM}_' \
                                  f'AdditionalNotes:{additionalnotesM}_' \
                                  f'CreatedByComputer:{createdbycomputerM}' \
                                  f'{dividerend}'

                    log[placeholder] = logcreation
                    overwrite = open(os.path.join(
                        open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles',
                                          "config.txt"),
                             'r').readlines()[2].strip('\n').split('=')[1], "MainLogFiles", f"{logfile}.txt"), 'w+')
                    overwrite.writelines(log)
                    overwrite.close()
                    print(f'log modified: \n\n{logcreation}\n')

    else:
        raise Exception('Error: function called with incorrect arguments. Please try again. ')


# make sure that initdir shows a list of files in MainLogFiles for easy selection. DONE
@click.command()
@click.argument('init', default=1)
def initialisefiledirectories(init):
    if init == 1:
        initialising = input('Would you like to initialise the main log directory to the default path '
                             '(folder location of ExerciseTerminal.py)? [y/N]: ')
        if initialising == 'y':
            click.echo('Initialising to default file path: ')
            currentdir = os.path.dirname(os.path.realpath(__file__))
            click.echo(currentdir)
        elif initialising == 'N':
            currentdir = input('Input the full directory path: ')
            currentdir = os.path.join(currentdir)
            click.echo(f'Checking if {currentdir} exists...')
            if os.path.isdir(currentdir):
                click.echo(f'Directory path {currentdir} saved to default. ')
            else:
                click.echo(f'{currentdir} does not exist. Please try again. ')
                return
        else:
            click.echo('Incorrect input. Please try again.')
            return

        ancillarydir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles")
        CreateRequiredFiles.checkdirexists(ancillarydir)
        CreateRequiredFiles.checklegendexists(ancillarydir)
        CreateRequiredFiles.checkconfigexists(ancillarydir, currentdir)

        maindir = os.path.join(currentdir, "MainLogFiles")
        CreateRequiredFiles.checkdirexists(maindir)

        configupdate = open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
            'r').readlines()
        configupdate[1] = f'Logging_to_File=None\n'
        configupdate[2] = f'Default_Directory={currentdir}\n'
        configupdatex = open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'w+')
        configupdatex.writelines(configupdate)
        configupdatex.close()

        CreateRequiredFiles.loaddestinationfile(currentdir, ancillarydir)

    else:
        click.echo('Files not initialised. To initialise, call default value 1.')


@click.command()
@click.argument('directory', type=click.Path(exists=True), required=True)
def changedefaultdir(directory):
    '''Changes the config file to match the custom directory; remember to change the logging file as well'''
    prompt = input(f'Change directory to: {click.format_filename(directory)}? [y/N]: ')
    if prompt == 'y':
        click.echo(f'Changing directory to: {click.format_filename(directory)}')
        #update config file - directory
        configupdate = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()
        configupdate[2] = f'Default_Directory={directory}\n'
        configupdatex = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'w+')
        configupdatex.writelines(configupdate)
        configupdatex.close()
        print('Process completed. Call "setlogfile" if you have not already done so. ')
    else:
        return


@click.command()
@click.argument('logfile', type=click.Path(exists=True), required=True)
def changeloggingfile(logfile):
    '''Changes the config file to match the custom logfile; remember to change the directory as well'''
    prompt = input(f'Change log file to: {click.format_filename(os.path.basename(logfile))}? [y/N]: ')
    if prompt == 'y':
        click.echo(f'Changing log file to: {click.format_filename(os.path.basename(logfile))}')
        #update config file - directory
        configupdate = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()
        configupdate[1] = f'Logging_to_File={os.path.splitext(os.path.basename(logfile))[0]}\n'
        configupdatex = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'w+')
        configupdatex.writelines(configupdate)
        configupdatex.close()
        print('Process completed. Call "setdir" if you have not already done so. ')
    else:
        return


@click.command()
@click.argument('reso', type=str, required=True)
def changereso(reso):
    '''Changes the "Logging_to_File" parameter to the desired resolution; only 4 supported; (1)"Day", (2)"12h", (3)"6h", (4)"3h"'''
    if reso in ('Day', '12h', '6h', '3h'):
        prompt = input(f'Change resolution to: {reso}? [y/N]: ')
        if prompt == 'y':
            click.echo(f'Changing resolution to: {reso}')
            #update config file - directory
            configupdate = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()
            configupdate[0] = f'Logging_Resolution={reso}\n'
            configupdatex = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'w+')
            configupdatex.writelines(configupdate)
            configupdatex.close()
            print('Process completed. Any "querylog" calls will reflect the new resolution. ')
        else:
            print('Aborted process! ')
            return
    else:
        raise Exception('Error: function only supports "Day", "12h", "6h" and "3h" resolutions. Please try again. ')


@click.command()
@click.option('-c', '--exercisename', prompt='What is the full name of your new exercise?', help='Recommended to use DASH in place of whitespaces if exercise-name so requires.'
                                                                                                'Ensure exercise name is not duplicate. ')
@click.option('-a', '--acronym', prompt='What is the acronym of your new exercise?', help='Ensure acronym is not duplicate. ')
def createnewexercise(exercisename, acronym):
    legend1 = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'r').readlines()
    findexercise = re.compile(exercisename)
    findacronym = re.compile(acronym)

    # check if exercise and acronym exists
    for i in legend1:
        if findexercise.match(i.split(':')[0]):
            print("Exercise already exists! Please try again. ")
            return
        else:
            pass

    for v in legend1:
        if findacronym.match(v.split(':')[1].strip('\n')):
            print("Acronym already exists! Please try again.")
            createnewexercise()
        else:
            pass

    # amendfile
    amendingline = f'{exercisename}:{acronym}\n'
    legend2 = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'a')
    legend2.write(amendingline)
    legend2.close()
    print('Exercise successfully added to legend.txt! ')

    # sort legend.txt
    sorting = input('Do you want to sort legend.txt alphabetically? [y/N]: ')
    if sorting == 'y':
        print('Sorting file alphabetically...')
        legend3 = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'r').readlines()
        legend3.sort()
        overwrite = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'w+')
        overwrite.writelines(legend3)
        overwrite.close()
        print('File sorted.')
    else:
        pass

    return exercisename

# delete exercise by acronym
@click.command()
@click.option('-d', '--deleteex', prompt='Type acronym (case-sensitive) of exercise you wish to delete; "CTRL+C" to abort', help='This function deletes an exercise referenced by its acronym from legend.txt.')
def deleteexercise(deleteex):
    legend = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"),
                  'r').readlines()
    exercisematcher = re.compile(f'^{deleteex}$')
    flag = False
    for i in legend:
        if exercisematcher.match(i.split(':')[1].strip('\n')):
            flag = not flag
            if click.confirm(f'Acronym "{deleteex}" is matched to the exercise "{i.split(":")[0]}". Delete?\n'
                             f'Bear in mind that deleting exercises may cause '
                             f'issues with exporting or modifying files, '
                             f'if previous logs record the deleted exercise.\n', abort=True):
                legend.remove(i)
                overwrite = open(
                    os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'w+')
                overwrite.writelines(legend)
                overwrite.close()
                print(f'{i}Deleted successfully.')
        else:
            pass
    if flag == False:
        print('Exercise does not exist for that acronym.')
    return

# find out the full exercise name from the acronym.
@click.command()
@click.option('-nm', '--check-name', prompt='What is the exercise acronym (case-sensitive)?', help='You must have the case-sensitive exercise acronym to utilise this function.')
def check_exnameexercise(check_name):
    legend = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"),
                  'r').readlines()
    regexacronym = re.compile(f'^{check_name}$')
    flag = False
    for i in legend:
        if regexacronym.match(i.split(':')[1].strip('\n')):
            flag = not flag
            print(f'Acronym "{check_name}" is matched to the exercise "{i.split(":")[0]}"')
        else:
            pass
    if flag == False:
        print('Exercise does not exist for that acronym.')
    return


# find out the exercise acronym from the full exercise name.
@click.command()
@click.option('-ac', '--check-acr', prompt='What is the full exercise name (case-sensitive)?', help='You must have the full and case-sensitive exercise name to utilise this function.')
def check_acronym(check_acr):
    legend = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"),
                  'r').readlines()
    regexname = re.compile(f'^{check_acr}$')
    flag = False
    for i in legend:
        if regexname.match(i.split(':')[0]):
            flag = not flag
            print('Exercise name "{}" has acronym "{}"'.format(check_acr, i.split(":")[1].strip("\n")))
        else:
            pass
    if flag == False:
        print('Acronym does not exist for that exercise.')
    return


@click.command()
@click.option('-d', '--querydate', prompt='Input date period to extract logs; format: \n'
                                          '(1)Day: ddmmyyyy_ddmmyyyy\n'
                                          '(2)12h, 6h, 3h: ddmmyyyy-HHMM_ddmmyyyy-HHMM\n', help='format: '
                                          '(1)Day: ddmmyyyy_ddmmyyyy'
                                          '(2)12h, 6h, 3h: ddmmyyyy-HHMM_ddmmyyyy-HHMM ')
def showlog(querydate):
    checkreso = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()
    resolution = checkreso[0].split('=')[1].strip('\n')
    logfile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                   'r').readlines()[1].strip('\n').split('=')[1]
    checkformatDAY = re.compile('^\d{8}[_]\d{8}$')
    checkformatOTHER = re.compile('^\d{8}[-]\d{4}[_]\d{8}[-]\d{4}$')
    logcompiler = []

    # check resolution, then continue to collect logs from log file
    if resolution in ('Day', '12h', '6h', '3h'):
        if checkformatDAY.match(querydate):

            # check if queried time input is valid --> raise exception for invalid input!
            timeerror = re.search('^(\d\d)(\d\d)(\d{4})[_](\d\d)(\d\d)(\d{4})$', querydate)
            try:
                if int(timeerror.group(1)) <= 0 or int(timeerror.group(1)) > 31 or int(timeerror.group(2)) <= 0 or int(
                        timeerror.group(2)) > 12 or int(timeerror.group(3)) > dt.datetime.now().year or int(
                        timeerror.group(4)) <= 0 or int(timeerror.group(4)) > 31 or int(timeerror.group(5)) <= 0 or int(
                        timeerror.group(5)) > 12 or int(timeerror.group(6)) > dt.datetime.now().year:
                    raise Exception('Error: incorrect date given. Please check date and try again. ')
            except AttributeError:
                raise Exception('Error: invalid date format. Please check date input and try again. ')

            # continue to collect logs
            print(f'Querying "{resolution}" resolution')
            startdate = querydate.split('_')[0]
            enddate = querydate.split('_')[1]
            log = open(os.path.join(
                open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                     'r').readlines()[2].strip('\n').split('=')[1], "MainLogFiles", f"{logfile}.txt"), 'r').readlines()
            for i in log:
                if i == 'n':
                    print('A blank line in the log file has been detected. Please delete this manually. ')
                    return
                else:
                    if dt.datetime.strptime(startdate, '%d%m%Y') <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M') <= dt.datetime.strptime(enddate, '%d%m%Y').replace(hour=23, minute=59):
                        if resolution == 'Day':
                            n = ['Day:1', i] # dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').strftime('%d%m%Y')
                            logcompiler.append(n)
                        elif resolution == '12h':
                            if dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 12:
                                period = '12h:1'
                            else:
                                period = '12h:2'
                            n = [period, i]
                            logcompiler.append(n)
                        elif resolution == '6h':
                            if dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 6:
                                period = '6h:1'
                            elif 6 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 12:
                                period = '6h:2'
                            elif 12 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 18:
                                period = '6h:3'
                            else:
                                period = '6h:4'
                            n = [period, i]
                            logcompiler.append(n)
                        elif resolution == '3h':
                            if dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 3:
                                period = '3h:1'
                            elif 3 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 6:
                                period = '3h:2'
                            elif 6 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 9:
                                period = '3h:3'
                            elif 9 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 12:
                                period = '3h:4'
                            elif 12 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 15:
                                period = '3h:5'
                            elif 15 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 18:
                                period = '3h:6'
                            elif 18 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 21:
                                period = '3h:7'
                            else:
                                period = '3h:8'
                            n = [period, i]
                            logcompiler.append(n)
                    else:
                        pass

            if not logcompiler:
                print('No logs for that time period. Please check date and try again. ')
                return
            else:
                print(f'Collected {len(logcompiler)} log file(s): \n')
                logcompiler.sort(key=takeTimefromloglistoflist)
                for line in logcompiler:
                    print(*line)
            intentexport = input('Do you want to export these logs to .csv? [y/N]: ')
            if intentexport == 'y':
                exporttocsv(logcompiler)
            else:
                return

        elif checkformatOTHER.match(querydate):
            # check if queried time input is valid --> raise exception for invalid input!
            timeerror = re.search('^(\d\d)(\d\d)(\d{4})[-](\d\d)(\d\d)[_](\d\d)(\d\d)(\d{4})[-](\d\d)(\d\d)$', querydate)
            try:
                if int(timeerror.group(1)) <= 0 or int(timeerror.group(1)) > 31 or int(timeerror.group(2)) <= 0 or int(
                        timeerror.group(2)) > 12 or int(timeerror.group(3)) > dt.datetime.now().year or int(
                        timeerror.group(4)) <= 0 or int(timeerror.group(4)) > 23 or int(timeerror.group(5)) < 0 or int(
                        timeerror.group(5)) > 59 or int(timeerror.group(6)) <= 0 or int(timeerror.group(6)) > 31 or int(
                        timeerror.group(7)) <= 0 or int(
                        timeerror.group(7)) > 12 or int(timeerror.group(8)) > dt.datetime.now().year or int(
                        timeerror.group(9)) <= 0 or int(timeerror.group(9)) > 23 or int(timeerror.group(10)) < 0 or int(
                        timeerror.group(10)) > 59:
                    raise Exception('Error: invalid date format. Please check date input and try again. ')
            except AttributeError:
                raise Exception('Error: invalid date format. Please check date input and try again. ')

            # continue to collect logs
            print(f'Querying "{resolution}" resolution')
            startdate = querydate.split('_')[0]
            enddate = querydate.split('_')[1]
            log = open(os.path.join(
                open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                     'r').readlines()[2].strip('\n').split('=')[1], "MainLogFiles", f"{logfile}.txt"), 'r').readlines()
            for i in log:
                if dt.datetime.strptime(startdate, '%d%m%Y-%H%M') <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M') <= dt.datetime.strptime(enddate, '%d%m%Y-%H%M'):
                    if resolution == 'Day':
                        n = ['Day:1', i]
                        logcompiler.append(n)
                    elif resolution == '12h':
                        if dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 12:
                            period = '12h:1'
                        else:
                            period = '12h:2'
                        n = [period, i]
                        logcompiler.append(n)
                    elif resolution == '6h':
                        if dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 6:
                            period = '6h:1'
                        elif 6 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 12:
                            period = '6h:2'
                        elif 12 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 18:
                            period = '6h:3'
                        else:
                            period = '6h:4'
                        n = [period, i]
                        logcompiler.append(n)
                    elif resolution == '3h':
                        if dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 3:
                            period = '3h:1'
                        elif 3 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 6:
                            period = '3h:2'
                        elif 6 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 9:
                            period = '3h:3'
                        elif 9 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 12:
                            period = '3h:4'
                        elif 12 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 15:
                            period = '3h:5'
                        elif 15 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 18:
                            period = '3h:6'
                        elif 18 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 21:
                            period = '3h:7'
                        else:
                            period = '3h:8'
                        n = [period, i]
                        logcompiler.append(n)
                else:
                    pass

            if not logcompiler:
                print('No logs for that time period. Please check date and try again. ')
                return
            else:
                print(f'Collected {len(logcompiler)} log file(s): \n')
                logcompiler.sort(key=takeTimefromloglistoflist)
                for line in logcompiler:
                    print(*line)

            intentexport = input('Do you want to export these logs to .csv? [y/N]: ')
            if intentexport == 'y':
                exporttocsv(logcompiler)
            else:
                return

        else:
            raise Exception('Error: incorrect input format for period; format should match: \n'
                            '(1)Day: ddmmyyyy_ddmmyyyy\n'
                            '(2)12h, 6h, 3h: ddmmyyyy-HHMM_ddmmyyyy-HHMM\n')
    else:
        raise Exception('Error: function only supports "Day", "12h", "6h" and "3h" resolutions. '
                        'Set the appropriate resolution through "setreso" and try again. ')


@click.command()
@click.argument('all', default=1)
def queryalllogs(all):
    '''prints all logs of selected file in sorted form.'''
    if all == 1:
        checkreso = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                         'r').readlines()
        resolution = checkreso[0].split('=')[1].strip('\n')
        logfile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                       'r').readlines()[1].strip('\n').split('=')[1]
        log = open(os.path.join(
            open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                 'r').readlines()[2].strip('\n').split('=')[1], "MainLogFiles", f"{logfile}.txt"), 'r').readlines()
        logcompiler = []
        for i in log:
            if i == '\n':
                print('A blank line in the log file has been detected. Please delete this manually. ')
                return
            else:
                if resolution == 'Day':
                    n = ['Day:1', i]
                    logcompiler.append(n)
                elif resolution == '12h':
                    if dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 12:
                        period = '12h:1'
                    else:
                        period = '12h:2'
                    n = [period, i]
                    logcompiler.append(n)
                elif resolution == '6h':
                    if dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 6:
                        period = '6h:1'
                    elif 6 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 12:
                        period = '6h:2'
                    elif 12 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 18:
                        period = '6h:3'
                    else:
                        period = '6h:4'
                    n = [period, i]
                    logcompiler.append(n)
                elif resolution == '3h':
                    if dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 3:
                        period = '3h:1'
                    elif 3 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 6:
                        period = '3h:2'
                    elif 6 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 9:
                        period = '3h:3'
                    elif 9 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 12:
                        period = '3h:4'
                    elif 12 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 15:
                        period = '3h:5'
                    elif 15 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 18:
                        period = '3h:6'
                    elif 18 <= dt.datetime.strptime(i.split('_')[0].split(':')[1], '%d%m%Y-%H%M').hour < 21:
                        period = '3h:7'
                    else:
                        period = '3h:8'
                    n = [period, i]
                    logcompiler.append(n)

        if not logcompiler:
            print(f'No logs in file {logfile}.txt. Please check date and try again. ')
            return
        else:
            print(f'Collected {len(logcompiler)} log file(s): \n')
            logcompiler.sort(key=takeTimefromloglistoflist)
            for line in logcompiler:
                print(*line)

        # ask if want to export
        intentexport = input('Do you want to export these logs to .csv? [y/N]: ')
        if intentexport == 'y':
            exporttocsv(logcompiler)
        else:
            return


@click.command()
@click.argument('sort', default=1)
def sortlogfile(sort):
    if sort == 1:
        logfile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
             'r').readlines()[1].strip('\n').split('=')[1]
        prompt = input(f'Sort log file "{logfile}.txt" by date and time? [y/N]: ')
        if prompt == 'y':
            print(f'Sorting file "{logfile}.txt"...')
            log = open(os.path.join(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()[2].strip('\n').split('=')[1], "MainLogFiles", f"{logfile}.txt"), 'r').readlines()
            log.sort(key=takeTimefromlog)
            overwrite = open(os.path.join(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()[2].strip('\n').split('=')[1], "MainLogFiles", f"{logfile}.txt"), 'w+')
            overwrite.writelines(log)
            overwrite.close()
            print('File sorted.')
        else:
            print('Aborted process!')
            return
    else:
        return


@click.command()
@click.argument('sort', default=1)
def sortlegend(sort):
    if sort == 1:
        prompt = input('Sort legend by alphabetical order: \n'
                       '(a) Full name of exercise \n'
                       '(b) Acronym of exercise \n'
                       '(c) Abort \n'
                       'a/b/c: ')
        if prompt == 'a':
            print('Sorting file alphabetically (Full name of exercise)...')
            legend = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'r').readlines()
            legend.sort()
            overwrite = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'w+')
            overwrite.writelines(legend)
            overwrite.close()
            print('File sorted.')
        elif prompt == 'b':
            print('Sorting file alphabetically (Acronym of exercise)...')
            legend = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'r').readlines()
            legend.sort(key=takeAcronym)
            overwrite = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'w+')
            overwrite.writelines(legend)
            overwrite.close()
            print('File sorted.')
        else:
            print("Aborted process!")
            return
    else:
        return


@click.command()
@click.argument('show', default=1)
def printconfig(show):
    if show == 1:
        configupdate = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"),
                            'r').readlines()
        configupdate[0] = ' ' + configupdate[0]
        print('\n')
        print(*configupdate)
    else:
        return


def exporttocsv(logcompiler):
    destinationfolder = input('Input destination folder: ')
    if os.path.isdir(destinationfolder):
        filename = input('Input filename without extension: ')
        destinationfolder = os.path.join(destinationfolder)
        print(f"Exporting to folder {destinationfolder}...")
        a, b, c, d, e, f = logcompiler[0][1].split('_')
        a_column = re.search('[[]\w{5}[]](\w*)', a.split(':')[0]).group(1)
        dataframecolumns = [f'Period:{logcompiler[0][0].split(":")[0]}', a_column, b.split(':')[0], c.split(':')[0].split('/')[0], c.split(':')[0].split('/')[1], c.split(':')[0].split('/')[2], d.split(':')[0], e.split(':')[0], f.split(':')[0]]
        exporterdataframe = pd.DataFrame(columns=dataframecolumns)
        for i in range(len(logcompiler)):
            g = logcompiler[i][0]
            h, ii, j, k, l, m = logcompiler[i][1].split('_')
            period = g.split(':')[1]
            time = h.split(':')[1]
            exercise = ii.split(':')[1]
            repetitions = j.split(':')[1].split('/')[0]
            weight = j.split(':')[1].split('/')[1]
            duration = j.split(':')[1].split('/')[2]
            doneby = k.split(':')[1]
            additionalnotes = l.split(':')[1]
            createdbycomputer = re.search('(.*)[[]\w{3}[]]', m.split(':')[1]).group(1)
            exporterdataframe.loc[i] = period, time, exercise, repetitions, weight, duration, doneby, additionalnotes, createdbycomputer
        exporterdataframe.to_csv(os.path.join(destinationfolder, f'{filename}.csv'))
        print(f'Exporting completed. Check {destinationfolder}. ')
    else:
        raise Exception('Error: folder does not exist. Please try again. ')

    print(f"Exporting completed. Check{destinationfolder}.")


def takeAcronym(elem):
    return elem.split(':')[1].strip('\n')


def takeTimefromlog(elem):
    return dt.datetime.strptime(elem.split('_')[0].split(':')[1], '%d%m%Y-%H%M')


def takeTimefromloglistoflist(elem):
    return dt.datetime.strptime(elem[1].split('_')[0].split(':')[1], '%d%m%Y-%H%M')


if __name__ == '__main__':
    initialisefiledirectories()