import os
import numpy as np

from random import shuffle, seed

from config import Extensions


def extractBasename(filepath):
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)

    return name


def extractCategory(filepath):
    name = extractBasename(filepath)
    category = name.split("-")[0]

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


def walk(path, targetDir=None, targetFile=None, targetExtensions=None):
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
            if targetDir is not None and dir_ == targetDir:
                target = os.path.join(root, dir_)
                found["dirs"].append(splitPath(cutPart(target, path)))

        if targetFile is not None or targetExtensions is not None:
            for file in files:
                if file == targetFile:
                    key = "files"
                elif file.endswith(targetExtensions):
                    key = "extensions"
                else:
                    continue

                target = os.path.join(root, file)
                found[key].append(splitPath(cutPart(target, path)))

    return found


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