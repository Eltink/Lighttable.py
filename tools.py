import os
from PIL import Image, ImageTk, ExifTags
import rawpy # Necessary to read .arw files
import time
import re

def get_exif(filepath, gettag): # New version, using filepath and reading only the necessary
    if filepath.endswith('.ARW'):
        # For .ARW files, use rawpy to read the raw data and imageio to convert to RGB
        raw = rawpy.imread(filepath)
        rgb = raw.postprocess()

        img = Image.fromarray(rgb)
    else:
        img = Image.open(filepath)
    try:
        exif_data = img._getexif()
        if exif_data is not None:
            for k, v in exif_data.items():
                tag = ExifTags.TAGS.get(k)
                if tag == gettag:
                    return v
    except (AttributeError, KeyError):
        return None

def file_navigator(file_path, steps):
    # todo imagem 0000 nao existe
    directory, filename = os.path.split(file_path)
    file_prefix, file_format = filename.split('.')
    file_id = int(file_prefix[-4:])
    file_id += steps
    file_id = file_id % 10000
    new_filename = f"{file_prefix[:-4]}{file_id:04d}.{file_format}"
    new_file_path = os.path.join(directory, new_filename)
    return new_file_path

    # def v1(file_path, steps):
    #     directory, filename = os.path.split(file_path)
    #     file_name, file_extension = os.path.splitext(filename)
    #
    #     # Define regular expressions to match numeric parts in different naming structures
    #     patterns = [
    #         r'(\d+)',  # Matches a continuous sequence of digits
    #         r'_(\d+)_',  # Matches digits surrounded by underscores
    #         r'_0(\d+)',  # I have no idea what im doing
    #         r'(\d{8}_\d{6})',  # Matches date-time patterns (e.g., 20210517_075548)
    #         r'(\d{4}-\d{2}-\d{2})',  # Matches date patterns (e.g., 2021-05-17)
    #     ]
    #
    #     # Try each pattern to find a match
    #     for pattern in patterns:
    #         match = re.search(pattern, file_name)
    #         if match:
    #             numeric_part = match.group(1)
    #             break
    #     else:
    #         # If no numeric part is found, return the original file path
    #         print(f"No pattern was recognized on file_path {file_path}")
    #         return file_path
    #
    #     # Convert the numeric part to an integer and add steps
    #     try:
    #         numeric_value = int(numeric_part)
    #         numeric_value += steps
    #     except ValueError:
    #         # If the numeric part is not a valid integer, return the original file path
    #         return file_path
    #
    #     # Construct the new file name with the updated numeric part
    #     new_numeric_part = str(numeric_value)
    #     new_file_name = file_name.replace(numeric_part, new_numeric_part)
    #     new_file_path = os.path.join(directory, f"{new_file_name}{file_extension}")
    #
    #     return new_file_path
    #
    # # # Was still not working when file started with 00
    # # directory, filename = os.path.split(file_path)
    # #
    # # # Split the filename into prefix and suffix, limiting the split to 1 occurrence of '0'
    # # prefix, suffix = filename.split('0', 1)
    # #
    # # # Extract the numeric part from the suffix
    # # file_id = int(suffix.split('.')[0])
    # # total_files = 10000
    # # file_id += steps
    # #
    # # if file_id < 0:
    # #     file_id = (total_files - abs(file_id) % total_files) % total_files
    # # elif file_id >= total_files:
    # #     file_id = file_id % total_files
    # #
    # # new_filename = f"{prefix}0{str(file_id).zfill(4)}.JPG"
    # # new_file_path = os.path.join(directory, new_filename)
    # #
    # # return new_file_path
    #
    # ## Was not working when files had more than one zero
    # # directory, filename = os.path.split(file_path)
    # #
    # # # Split the filename into prefix and suffix
    # # prefix, suffix = filename.split('_' if '_' in filename else '0')
    # #
    # # # Extract the numeric part from the suffix
    # # file_id = int(suffix.split('.')[0])
    # #
    # # total_files = 10000
    # #
    # # file_id += steps
    # #
    # # if file_id < 0:
    # #     file_id = (total_files - abs(file_id) % total_files) % total_files
    # # elif file_id >= total_files:
    # #     file_id = file_id % total_files
    # #
    # # new_filename = f"{prefix}_{str(file_id).zfill(5)}.JPG"
    # # new_filename = new_filename.replace('_', '') if '_' not in filename else new_filename
    # # new_file_path = os.path.join(directory, new_filename)
    # #
    # # return new_file_path
    #
    # ##Was not working with files with format DSC01367.JPG
    # # directory, filename = os.path.split(file_path)
    # # prefix, suffix = filename.split('_')
    # # file_id = int(suffix.split('.')[0])
    # #
    # # total_files = 10000
    # # file_id += steps
    # #
    # # if file_id < 0:
    # #     file_id = (total_files - abs(file_id) % total_files) % total_files
    # # elif file_id >= total_files:
    # #     file_id = file_id % total_files
    # #
    # # new_filename = f"{prefix}_{str(file_id).zfill(5)}.JPG"
    # # new_file_path = os.path.join(directory, new_filename)
    # #
    # # return new_file_path
    # print(f"v1(file_path, steps): {v1(file_path, steps)}")
    # print(f"v2(file_path, steps): {v2(file_path, steps)}")
    # try:    return v2(file_path, steps)
    # except: return v1(file_path, steps)


debugging = 0
timing = 0

def is_it_showable(filepaths):
    gabarito = [0, 1, 1, 1, 0, 1, 0, 1, 0]
    len_filepaths = len(filepaths)
    bracketed   =   [None] * len_filepaths
    EV          =   [None] * len_filepaths
    mostra      =   [None] * len_filepaths
    threshold_EV = 0.9

    t0 = time.time()
    bracketed = [1 if get_exif(filepath, "ExposureMode") == 2 else 0 for filepath in filepaths]
    # a = get_exif(filepaths[0], "ExposureBiasValue")
    # print("tipo", type(get_exif(filepaths[0], "ExposureBiasValue")))
    # print("valor", (get_exif(filepaths[0], "ExposureBiasValue")))
    # print(f" a/b: {a.numerator}/{a.denominator}")
    EV = [float(get_exif(filepath, "ExposureBiasValue")) if get_exif(filepath, "ExposureBiasValue") is not None else 0 for filepath in filepaths]
    trace = [None] * len_filepaths
    if timing: print(f"Time to load metadata lists: {time.time()-t0} sec")

    if debugging: print("bracketed", bracketed)
    if debugging: print("EV", EV)

    # Initialize a list to store temporary values for mostra[i+1]
    temp_mostra = [None] * len_filepaths
    # v2 implementation
    if True:
        if debugging: print("\nv2 implementation")
        for i in range(len_filepaths):
            if not bracketed[i]: # From now on, all i are bracketed
                mostra[i] = 1
                trace[i] = "a"
            elif i == 0:  #
                if bracketed[i + 1]:
                    mostra[i] = 0  # It's the first of a series of brackets
                    trace[i] = "b"
            elif i == len_filepaths - 1:
                if not bracketed[i - 1]:
                    mostra[i] = 1  # It's an isolated bracketed
                    trace[i] = "c"
                if not mostra[i - 1]:
                    mostra[i] = 1  # It's an incomplete bracket or an unknown case (5 bracket)
                    trace[i] = "d"

        if debugging: print("mostra", mostra)
        # if debugging: print("sum(mostra)", sum(mostra))
        if debugging: print(f"There are {sum(1 for i, j in zip(mostra, gabarito) if i != j)} different elements.")

    # ChatGPT implementation
    if True:
        if debugging: print("\nChatGPT implementation")
        for i in range(len_filepaths):
            if not bracketed[i]:
                mostra[i] = 1
                trace[i] = "a"
            # From now on, all i are bracketed
            elif i == 0:
                if bracketed[i + 1]:
                    mostra[i] = 0
                    trace[i] = "b"
            elif i == len_filepaths - 1:
                if not bracketed[i - 1]:
                    mostra[i] = 1
                    trace[i] = "c"
                elif not mostra[i - 1]:
                    mostra[i] = 1
                    trace[i] = "d"
            elif not bracketed[i - 1] and not bracketed[i + 1]:
                mostra[i] = 1
                trace[i] = "e"
            elif not bracketed[i - 1] and bracketed[i + 1]:
                mostra[i] = 0
                trace[i] = "f"
            elif EV[i] == round((EV[i - 1] + EV[i + 1]) / 2, 1):
                mostra[i] = 1
                temp_mostra[i + 1] = 0  # Store temporary value for mostra[i+1]
                trace[i] = "h"
            elif EV[i - 1] > EV[i] and EV[i] < EV[i + 1]:
                mostra[i] = 0
                trace[i] = "k"
            elif abs((EV[i + 1] - EV[i]) - (EV[i] - EV[i - 1])) > threshold_EV:
                mostra[i] = 0
                trace[i] = "j"
            elif EV[i - 1] < EV[i] and EV[i] > EV[i + 1] and abs((EV[i + 1] - EV[i]) + (EV[i] - EV[i - 1])) <= threshold_EV:
                mostra[i] = 1
                trace[i] = "i"
            else:
                mostra[i] = "?"
                trace[i] = "l"
                print(f"\nCouldn't classify image i = {i}")
                print(f"B: {[bracketed[i - 2], bracketed[i - 1], bracketed[i], bracketed[i + 1]]}")
                print(f"EV: {[EV[i - 2], EV[i - 1], EV[i], EV[i + 1]]}")
                print(f"M: {[mostra[i - 2], mostra[i - 1], mostra[i], mostra[i + 1]]}")
                mostra[i] = 1

        # Update mostra with the temporary values
        for i in range(len_filepaths):
            if temp_mostra[i] is not None:
                mostra[i] = temp_mostra[i]
                trace[i] = "t"

        # if debugging: print("bracketed", bracketed)
        # if debugging: print("EV", EV)
        if debugging: print(trace)
        if debugging: print("mostra", mostra)
        if debugging: print("sum(mostra)", sum(mostra))
        if debugging: print(f"There are {sum(1 for i, j in zip(mostra, gabarito) if i != j)} different elements.")

    # Glauco implementation
    if True:
        if debugging: print("\nGlauco implementation")
        for i in range(len_filepaths):
            if not bracketed[i]:
                mostra[i] = 1
                trace[i] = "a"
            # From now on, all i are bracketed
            elif i == 0:  #
                if bracketed[i + 1]:
                    mostra[i] = 0  # It's the first of a series of brackets
                    trace[i] = "b"
            elif i == len_filepaths - 1:
                if not bracketed[i - 1]:
                    mostra[i] = 1  # It's an isolated bracketed
                    trace[i] = "c"
                if not mostra[i - 1]:
                    mostra[i] = 1  # It's an incomplete bracket or an unknown case (5 bracket)
                    trace[i] = "d"
            elif not bracketed[i - 1] and not bracketed[i + 1]:
                mostra[i] = 1  # It's an isolated bracketed
                trace[i] = "e"
            elif not bracketed[i - 1] and bracketed[i + 1]:
                mostra[i] = 0  # It's the first on a bracketing
                trace[i] = "f"
            # elif bracketed[i - 1] and not bracketed[i + 1]: #Seems to be clasifying wrong the end of a complete bracket
            #     mostra[i] = 1  # It's the second on a incomplete bracketing
            #     trace[i] = "g"
            elif EV[i] == round((EV[i-1] + EV[i+1])/2,1):
                mostra[i] = 1  # It's the middle of a bracketing. TODO extend for 5 brackets
                trace[i] = "h"
            elif EV[i - 1] > EV[i] and EV[i] < EV[i + 1]:
                mostra[i] = 0 # Its a local minimum: starting of a bracket
                trace[i] = "k"
            elif abs((EV[i+1]-EV[i]) - (EV[i] - EV[i-1])) > threshold_EV:  # Its the end of a complete bracket
                # print(f"EV[i-1] {EV[i-1]} EV[i] {EV[i]} EV[i+1] {EV[i+1]}")
                # print("abs((EV[i+1]-EV[i]) - (EV[i] - EV[i-1]))", abs((EV[i+1]-EV[i]) - (EV[i] - EV[i-1])))
                mostra[i] = 0
                trace[i] = "j"
            elif EV[i - 1] < EV[i] and EV[i] > EV[i + 1] and abs((EV[i+1]-EV[i]) + (EV[i] - EV[i-1])) <= threshold_EV:  # Center of an incomplete bracket
                mostra[i] = 1
                trace[i] = "i"
            else:
                mostra[i] = "?"
                trace[i] = "l"
                print(f"\nCouldn't classify image i = {i}")
                print(f"B: {[bracketed[i - 2], bracketed[i - 1], bracketed[i], bracketed[i + 1]]}")
                print(f"EV: {[EV[i - 2], EV[i - 1], EV[i], EV[i + 1]]}")
                print(f"M: {[mostra[i - 2], mostra[i - 1], mostra[i], mostra[i + 1]]}")
                mostra[i] = 1
        # if debugging: print("bracketed", bracketed)
        # if debugging: print("EV", EV)
        if debugging: print(trace)
        if debugging: print("mostra", mostra)
        if debugging: print("sum(mostra)", sum(mostra))
        if debugging: print(f"There are {sum(1 for i, j in zip(mostra, gabarito) if i != j)} different elements.")

    # Andressa implementation
    if True:
        if debugging: print("\nAndressa implementation")
        for i in range(len_filepaths):
            if bracketed[i] == False: # If its not bracketed, always show
                mostra[i] = 1
                trace = "b"
            # elif bracketed[i] == True: #because its always either True or False, we can simplify it
            else:
                if i == 0 and bracketed[i] and bracketed[i+1]: # If first two are bracketed, no need to show first one
                    mostra[i] = 0
                elif i == 0 or i == len_filepaths - 1: # If im at the borders of the list, return 1 (false positives are better)
                    mostra[i] = 1
                    trace = "c"
                else: # Current image is bracketed
                    if EV[i] == round((EV[i-1] + EV[i+1])/2,1): # If it's the average
                        mostra[i] = 1
                        trace = "d"
                    elif not bracketed[i-1] and EV[i+1]>EV[i]:
                        mostra[i]= 0
                        trace = "e"
                    elif mostra[i-1] and i!=1 and bracketed[i-1]: # because current is bracketed
                        mostra[i] = 0
                        trace = "h"
                    elif bracketed[i-1] and not mostra[i-1] and EV[i]>EV[i-1]:
                        mostra[i]=1
                        trace = "i"
                    elif not bracketed[i+1] and abs((EV[i+1]-EV[i]) - (EV[i] - EV[i-1])) <= threshold_EV: # Case for incomplete brackets
                        mostra[i] = 1
                        trace = "f"
                        print("This seemed to never be necessary. Please investigate.")
                        print("Filename: ", filepaths[i])
                    else:
                        mostra[i] = 0
                        trace = "g"
        if debugging: print(trace)
        if debugging: print("mostra", mostra)
        if debugging: print("sum(mostra)", sum(mostra))
        if debugging: print(f"There are {sum(1 for i, j in zip(mostra, gabarito) if i != j)} different elements.")

    if debugging: print("\nMedia implementation")
    mostra_edges = [None] * len_filepaths
    mostra_complete = [None] * len_filepaths
    mostra_incomplete = [None] * len_filepaths
    trace = [None] * len_filepaths

    for i in range(len_filepaths):
        if i == 0:  #
            if bracketed[i + 1]:
                mostra_edges[i] = 0  # It's the first of a series of brackets
        elif i == len_filepaths - 1:
            if not bracketed[i - 1]:
                mostra_edges[i] = 1  # It's an isolated bracketed
            if not mostra[i - 1]:
                mostra_edges[i] = 1  # It's an incomplete bracket or an unknown case (5 bracket)
        # Real start of the code
        elif bracketed[i]:
            # From now on, all i are bracketed
            if EV[i] == round((EV[i-1] + EV[i+1])/2, 1):  # todo extend media 5
                mostra_complete[i - 1] = 0
                mostra_complete[i]     = 1
                mostra_complete[i + 1] = 0
            elif EV[i - 1] > EV[i] and EV[i] < EV[i + 1]:  # Local minimum
                mostra_incomplete[i] = 0
                mostra_incomplete[i + 1] = 1
                trace[i] = "i"
            else: # Images are a B=110, so M=1; or local maximum on an incomplete bracket, M=1
                mostra_incomplete[i] = 1
                # trace[i] = "j"
                # print(f"Couldnt classify image i={i}")
                # print(f"B: {[bracketed[i - 1], bracketed[i], bracketed[i + 1]]}")
                # print(f"EV: {[EV[i - 1], EV[i], EV[i + 1]]}")
                # print(f"M: {[mostra[i - 1], mostra[i], mostra[i + 1]]}")

    for i in range(len_filepaths):
        if not bracketed[i]:
            mostra[i] = 1
        elif mostra_complete[i] is not None:
            mostra[i] = mostra_complete[i]
        elif mostra_edges[i] is not None:
            mostra[i] = mostra_edges[i]
        elif mostra_incomplete[i] is not None:
            mostra[i] = mostra_incomplete[i]
        else:
            print(f"Didnt fall in any case: i={i}")
            print(f"B: {[bracketed[i - 1], bracketed[i], bracketed[i + 1]]}")
            print(f"EV: {[EV[i - 1], EV[i], EV[i + 1]]}")
            print(f"M: {[mostra[i - 1], mostra[i], mostra[i + 1]]}")

    # if debugging: print(trace)
    if debugging: print("mostra", mostra)
    if debugging: print("sum(mostra)", sum(mostra))
    if debugging: print(f"There are {sum(1 for i, j in zip(mostra, gabarito) if i != j)} different elements.")
    if debugging:
        for i, (m, g) in enumerate(zip(mostra, gabarito)):
            # zip aggregates vectors element-wise into tuples.
            # Enumerate loops over the elements of an iterable, keeping track of the current index
            # e.g. [(0, (a, A)), (1, (b, B)), (2, (c, C))...]
            if m != g:
                print(f"Output differs from gabarito at index {i}: Expected={g}, Got={m}")
                if i not in [0, len_filepaths - 1]:
                    print(f"B: {[bracketed[i - 1], bracketed[i], bracketed[i + 1]]}")
                    print(f"EV: {[EV[i - 1], EV[i], EV[i + 1]]}")
                    print(f"M: {[mostra[i - 1], mostra[i], mostra[i + 1]]}")
    return mostra

def get_destination_dir(source_dir):
    # Get the parent directory of the source directory
    parent_dir = os.path.dirname(source_dir)

    # Get the name of the last subdirectory in the source directory
    subdirectories = os.path.split(source_dir)
    last_subdirectory = subdirectories[-1]

    # Create the destination directory path in the parent directory
    destination_dir = os.path.join(parent_dir, last_subdirectory + ' sel')

    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    return destination_dir

def wanted_files(dir): #Legacy function, currently not being used
    files = os.listdir(dir)
    EV = [exif(file, "ExposureBiasValue") for file in files]
    neutral_files = []
    for i in range(1, len(files) - 1):
        if EV[i] == (EV[i - 1] + EV[i + 1]) / 2:
            neutral_files.append(files[i])
    non_bracketed = []
    for file in files:
        if exif(file, "ExposureMode") == 0:
            non_bracketed.append(file)
    return neutral_files

def exif(filename, gettag): #Legacy function, currently not being used
    img = Image.open(os.path.join(source_dir, filename))
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
        #print(exif_table)
        return exif_table.get(gettag)
    except (AttributeError, KeyError):
        return None