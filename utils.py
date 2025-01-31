import os
import shutil
import json
import numpy as np

from random import shuffle, seed
from colorama import Fore, Back, Style

from config import Extensions, Constants as const


def extractBasename(filepath):
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)

    return name


def extractCategory(filepath):
    name = extractBasename(filepath)
    category = name.split(const.separator)[0]

    return category, name


def openJsonSafely(path):
    try:
        j = json.load(open(path, "r"))
    except:
        j = {}

    return j


def extendName(basename, extension):
    return basename + extension


def changeExtension(path, extension):
    path, _ = os.path.splitext(path)
    return extendName(path, extension)


def makeJSONname(basename):
    return extendName(basename, Extensions.json)


def makeMOVname(basename):
    return extendName(basename, Extensions.mov)


def makeXMLname(basename):
    return extendName(basename, Extensions.xml)


def matchLists(master, slave, transformer:callable=None, getMismatched=False, showMessages=False):
    transformer = transformer if transformer is not None else lambda x: x

    matched = []
    mismatched = []
    for element in slave:
        if transformer(element) not in master:
            mismatched.append(element)
            if showMessages:
                print(f"{Fore.RED}No matched element for {element} {Style.RESET_ALL}")
        else:
            matched.append(element)

    return matched if not getMismatched else (matched, mismatched)


def readLines(path):
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        lines = f.readlines()

    lines = [l.strip() for l in lines]

    return lines


def writeLines(lines, path):
    lines = [line + "\n" for line in lines]

    with open(path, "w") as f:
        f.writelines(lines)


def safeNesting(nesting):
    def wrapper(*args, **kwargs):
        kwargs["keys"] = kwargs["keys"].copy()
        return nesting(*args, **kwargs)
    return wrapper


@safeNesting
def putNested(dictionary, keys, value):
    key = keys.pop(0)

    if not keys:
        dictionary[key] = value
    else:
        dictionary[key] = dictionary.get(key, {})
        putNested(dictionary=dictionary[key], keys=keys, value=value)


@safeNesting
def updateNested(dictionary, keys, value):
    key = keys.pop(0)

    if not keys:
        try:
            dictionary[key] += value
        except KeyError:
            dictionary[key] = value
    else:
        dictionary[key] = dictionary.get(key, {})
        updateNested(dictionary=dictionary[key], keys=keys, value=value)


@safeNesting
def getNested(dictionary, keys, default=None):
    key = keys.pop(0)

    if not keys:
        return dictionary.get(key, default)
    elif not dictionary:
        return default
    else:
        return getNested(dictionary=dictionary.get(key, {}), keys=keys, default=default)


# def getFromAbyss(dictionary, levels=None, keySet=None):
#     keySet = [] if keySet is None else keySet
#
#     if isinstance(dictionary, dict):
#         if levels is None or len(keySet) != levels:
#             for key, value in dictionary.items():
#                 yield getFromAbyss(value, levels, keySet + [key])
#         else:
#             yield keySet


def walk(path, targetDirs:(tuple, str)=None, targetFiles:(tuple, str)=None, targetExtensions:(tuple, str)=None):
    targetDirs = (targetDirs) if not isinstance(targetDirs, (tuple, list)) else targetDirs
    targetFiles = (targetFiles) if not isinstance(targetFiles, (tuple, list)) else targetFiles

    found = {
        "root": path,
        "dirs": [],
        "files": [],
        "extensions": []
    }

    seekInFiles = targetFiles is not None or targetExtensions is not None

    path = os.path.normcase(path)

    def cutPart(path, part):
        return path.replace(part, "")

    def splitPath(path):
        return path.split(os.path.sep)[1:]

    for root, dirs, files in os.walk(path):
        for dir_ in dirs:
            if targetDirs is not None and dir_ in targetDirs:
                target = os.path.join(root, dir_)
                found["dirs"].append(splitPath(cutPart(target, path)))

        if seekInFiles:
            for file in files:
                if targetFiles is not None and file in targetFiles:
                    key = "files"
                elif targetExtensions is not None and file.endswith(targetExtensions):
                    key = "extensions"
                else:
                    continue

                target = os.path.join(root, file)
                found[key].append(splitPath(cutPart(target, path)))

    return found


def listFilesFromDir(path, targetFiles:tuple=None, targetExtensions:tuple=None):
    targetFiles = () if targetFiles is None else targetFiles
    targetExtensions = () if targetExtensions is None else targetExtensions

    files = os.listdir(path)
    files = [f for f in files if os.path.isfile(os.path.join(path, f))]

    if targetFiles:
        files = [f for f in files if f in targetFiles]

    if targetExtensions:
        files = [f for f in files if any(f.endswith(ext) for ext in targetExtensions)]

    return files


def clean(path, through=False, targetFiles:tuple=None, targetExtensions:tuple=None):
    if targetFiles is None and targetExtensions is None and through:
        shutil.rmtree(path)

    targetFiles = () if targetFiles is not None else targetFiles

    total = 0

    if through:
        files = walk(path, targetFiles=targetFiles, targetExtensions=targetExtensions)
        filesList = []
        filesList.extend(files.get("files", []))
        filesList.extend(files.get("extensions", []))

        files = [os.path.join(files.get("root"), *f) for f in filesList]
    else:
        files = listFilesFromDir(path, targetFiles=targetFiles, targetExtensions=targetExtensions)
        files = [os.path.join(path, f) for f in files]

    for filePath in files:
        try:
            os.unlink(filePath)
            total += 1
        except Exception as e:
            print(f"{Fore.RED}Couldn't unlink {filePath} because of error: {e} {Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}Unlinked {total} files in total {Style.RESET_ALL}")


def permutate(arr, saveOrder=False, seedValue=1234):
    idxs = [i for i in range(len(arr))]
    if saveOrder:
        seed(seedValue)

    shuffle(idxs)

    if isinstance(arr, np.ndarray):
        arr = arr[idxs]
    elif isinstance(arr, list):
        arr = [arr[idx] for idx in idxs]
    else:
        raise TypeError

    return arr