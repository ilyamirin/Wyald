import os
import shutil
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


def makeJSONname(basename):
    return basename + Extensions.json


def makeMOVname(basename):
    return basename + Extensions.mov


def putNested(dictionary, keys, value):
    key = keys.pop(0)

    if not keys:
        dictionary[key] = value
    else:
        dictionary[key] = dictionary.get(key, {})
        putNested(dictionary[key], keys, value)


def updateNested(dictionary, keys, value):
    key = keys.pop(0)

    if not keys:
        try:
            dictionary[key] += value
        except KeyError:
            dictionary[key] = value
    else:
        dictionary[key] = dictionary.get(key, {})
        putNested(dictionary[key], keys, value)


def walk(path, targetDirs:(tuple, str)=None, targetFiles:(tuple, str)=None, targetExtensions:(tuple, str)=None):
    targetDirs = (targetDirs) if not isinstance(targetDirs, (tuple, list)) else targetDirs
    targetFiles = (targetFiles) if not isinstance(targetFiles, (tuple, list)) else targetFiles

    found = {
        "root": path,
        "dirs": [],
        "files": [],
        "extensions": []
    }

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

        if targetFiles is not None or targetExtensions is not None:
            for file in files:
                if file in targetFiles:
                    key = "files"
                elif file.endswith(targetExtensions):
                    key = "extensions"
                else:
                    continue

                target = os.path.join(root, file)
                found[key].append(splitPath(cutPart(target, path)))

    return found


def listFilesFromDir(path, targetFiles:tuple=None, targetExtensions:tuple=None):
    targetFiles = () if targetFiles is not None else targetFiles
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

        files = [os.path.join([files.get("root")] + f) for f in filesList]
    else:
        files = listFilesFromDir(path, targetFiles=targetFiles, targetExtensions=targetExtensions)
        files = [os.path.join(path, f) for f in files]

    for filePath in files:
        try:
            os.unlink(filePath)
            total += 1
        except Exception as e:
            print(f"{Fore.RED} Couldn't unlink {filePath} because of error: {e} {Style.RESET_ALL}")

    print(f"\n{Fore.GREEN} Unlinked {total} files in total {Style.RESET_ALL}")


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