import os
import re

def checkdirexists(dirname):
    if not os.path.isdir(dirname):
        try:
            os.mkdir(dirname)
            print("Successfully created the directory {} ".format(dirname))
        except OSError:
            print("Creation of the directory {} failed".format(dirname))
            os.system('pause')
    else:
        print("Directory {} exists".format(dirname))

def checklegendexists(dirname):
    legendexists = os.path.isfile(os.path.join(dirname, "legend.txt"))
    if not legendexists:
        try:
            legend = open(os.path.join(dirname, "legend.txt"), 'w')
            L = ['PistolSquats:PS\n', 'Benchpress:BP\n', 'Pushups:PU\n', 'Planks:PL\n',
                 'Jogging/Running:Rn\n', 'Pullups:Pu\n', 'Situps:Su\n', 'Crunches:Cr\n',
                 'BicepCurlAlternating:BCA\n', 'BicepCurlSimultaneous:BCS\n']
            L.sort()
            legend.writelines(L)
            legend.close()
            print("Successfully created the file {} ".format(os.path.join(dirname, "legend.txt")))
        except Exception as ex:
            print("Creation of file legend.txt failed; error {}".format(str(ex)))
    else:
        print('legend.txt exists')

def checkconfigexists(dirname, currentdir):
    defaultsexists = os.path.isfile(os.path.join(dirname, "config.txt"))
    if not defaultsexists:
        try:
            defaults = open(os.path.join(dirname, "config.txt"), 'w')
            L = ['Logging_Resolution=Day\n', 'Logging_to_File=None\n', 'Default_Directory={}\n'.format(currentdir)]
            defaults.writelines(L)
            defaults.close()
            print("Successfully created the file {} ".format(os.path.join(dirname, "config.txt")))
        except Exception as ex:
            print("Creation of file config.txt failed; error {}".format(str(ex)))
    else:
        print('config.txt exists')


def loaddestinationfile(dirname, ancillarydir):
    print(f'Logging directory selected: {dirname}')
    defaults = open(os.path.join(ancillarydir, "config.txt"), 'r')
    destinationfile = defaults.readlines()[1].strip('\n').split('=')[1]
    defaults.close()
    if destinationfile == 'None':
        print('No logging file selected. Files in MainLogFile folder of selected directory: ')
        print('\n'.join(os.listdir(os.path.join(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AncillaryFiles', "config.txt"), 'r').readlines()[2].strip('\n').split('=')[1], 'MainLogFiles'))))
        selectedfilename = input('Type in name of logging filename without extension; if file does not exists, '
                                 'this file will be created '
                                 '(it is recommended to name the file after the person whose activities are logged):\n')
        if selectedfilename and os.path.isfile(os.path.join(dirname, "MainLogFiles", f"{selectedfilename}.txt")):
            file1 = open(os.path.join(ancillarydir, "config.txt"), 'r')
            fileoverwrite = file1.readlines()
            fileoverwrite[1] = f'Logging_to_File={selectedfilename}\n'
            selectedfile = open(os.path.join(ancillarydir, "config.txt"), 'w+')
            selectedfile.writelines(fileoverwrite)
            selectedfile.close()
            print(f'{selectedfilename}.txt selected. ')
        elif selectedfilename and not os.path.isfile(os.path.join(dirname, "MainLogFiles", f"{selectedfilename}.txt")):
            print(f'{selectedfilename} does not exist. Creating and selecting file...')
            createdfile = open(os.path.join(dirname, "MainLogFiles", f"{selectedfilename}.txt"), 'w')
            createdfile.close()
            file1 = open(os.path.join(ancillarydir, "config.txt"), 'r')
            fileoverwrite = file1.readlines()
            fileoverwrite[1] = f'Logging_to_File={selectedfilename}\n'
            selectedfile = open(os.path.join(ancillarydir, "config.txt"), 'w+')
            selectedfile.writelines(fileoverwrite)
            selectedfile.close()
            print(f'{selectedfilename} created and selected')
        elif not selectedfilename:
            print('No input. Please try again.')
    else:
        if os.path.isfile(os.path.join(dirname, "MainLogFiles", f"{destinationfile}.txt")):
            print(f'Logging file selected: {destinationfile}')
        else:
            print('Selected logging file does not exist. ')
            file1 = open(os.path.join(ancillarydir, "config.txt"), 'r')
            fileoverwrite = file1.readlines()
            fileoverwrite[1] = f'Logging_to_File=None\n'
            selectedfile = open(os.path.join(ancillarydir, "config.txt"), 'w+')
            selectedfile.writelines(fileoverwrite)
            selectedfile.close()
            loaddestinationfile(dirname, ancillarydir) # after overwriting defaults, call loaddestination again.


# call without decorator
def createnewexercise_nodecorator(exercisename, acronym):
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
        else:
            pass

    # amendfile
    amendingline = f'{exercisename}:{acronym}\n'
    legend2 = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'a')
    legend2.write(amendingline)
    legend2.close()
    print('Exercise successfully added to legend.txt! ')

    # sort legend.txt
    sorting = input('Do you want to sort legend.txt alphabetically? y/n: ')
    if sorting == 'y':
        print('Sorting file alphabetically...')
        legend3 = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'r')
        fileoverwrite = legend3.readlines()
        legend3.close()
        fileoverwrite.sort()
        overwrite = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "AncillaryFiles", "legend.txt"), 'w+')
        overwrite.writelines(fileoverwrite)
        overwrite.close()
        print('File sorted.')
    else:
        pass

    return exercisename