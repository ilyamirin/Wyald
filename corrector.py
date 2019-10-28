import  os

import json

from config import Path, Constants


Categories = dict()


def parseCategories(path):
    res = []
    with open(path, "r") as file:
        for line in file.readlines():
            res.extend(line.rstrip().split(' '))
    return res


def fixCategoriesIndices(ctgList):
    correctIdx = 0
    for idx, ctg in enumerate(ctgList):
        if idx == 60:
            continue
        Categories[ctg] = correctIdx
        correctIdx += 1


def prettifyNamesLegacy(path):
    import os
    for filename in os.listdir(path):
        s = filename.replace("-", "_")
        pos = s.rfind('_')
        s = list(s)
        s[pos] = '-'
        newName = "".join(s)
        os.rename(os.path.join(path, filename), os.path.join(path, newName))


def prettifyNames(path):
    renamedFiles = dict()
    for dir in os.listdir(path):
        if os.path.isdir(os.path.join(path, dir)) and not dir in renamedFiles:

            partName = dir.split("_red.")
            if len(partName) < 2:
                continue

            newName = partName[1]

            os.rename(os.path.join(path, dir), os.path.join(path, newName))
            os.rename(os.path.join(path, f"{dir}.mp4"), os.path.join(path, f"{newName}.mp4"))
            renamedFiles[dir] = newName


categories = dict()
renamedFiles = []
def prettifyVideoNames(path):
    with open(os.path.join(path, "correct_names.txt"), "r") as fin:
        names = fin.readlines()
        for name in names:
            oldName, newName = tuple(name.split())
            oldName = oldName.rsplit('_', 1)
            print(f"{oldName} {newName}")
            categories[oldName[0]] = newName

    for videoFile in os.listdir(path):
        if not videoFile.endswith("MOV"):
            continue
        videoFile, ext = os.path.splitext(videoFile)
        videoFile, versionFile = tuple(videoFile.rsplit('-', 1))
        if not videoFile in categories and not videoFile in renamedFiles:
            os.remove(os.path.join(path, f"{videoFile}-{versionFile}.MOV"))
            os.remove(os.path.join(path, "annotation", f"{videoFile}-{versionFile}.json"))
            continue
        renamedFiles.append(categories[videoFile])
        os.rename(os.path.join(path, f"{videoFile}-{versionFile}.MOV"), os.path.join(path, f"{categories[videoFile]}-{versionFile}.MOV"))
        os.rename(os.path.join(path, 'annotation', f"{videoFile}-{versionFile}.json"), os.path.join(path, 'annotation', f"{categories[videoFile]}-{versionFile}.json"))

        
def fixJsons():
    import os
    from utils import walk, readLines

    categories = readLines(Path.categories)
    jsons = walk(Path.dataset, targetFiles="marks.json").get("files")

    for i, jsn in enumerate(jsons):
        print(f"\rProcessing {i} json file", end="")

        path = os.path.join(Path.dataset, *jsn)
        marks = json.load(open(path, "r"))
        for name, items in marks.items():
            ctgIdx = categories.index(items[Constants.fullCategory])
            items[Constants.ctgIdx] = ctgIdx

        json.dump(marks, open(path, "w"), indent=4)


def updateCategory(path):
    for filename in os.listdir(path):
        res = {}
        with open(os.path.join(path, filename), "r") as jsonFile:
            jdata = json.load(jsonFile)
            catName, _ = filename.rsplit('-', 1)
            for frame in jdata:
                res[frame] = {
                    "category": catName,
                    "coordinates": jdata[frame]["coordinates"]
                }
            jsonFile.close()

        with open(os.path.join(path, filename), "w") as jsonFile:
            json.dump(res, jsonFile, indent=4)


def main():
    pass


if __name__ == "__main__":
    main()