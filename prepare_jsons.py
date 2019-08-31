import os
import json

from colorama import Fore, Style

from utils import openJsonSafely, extractCategory, makeJSONname, putNested
from config import Path, Extensions, Constants as const


def getKeysOffset(keys):
    keys = list(keys)
    offset = min([getFrameNumber(l) for l in keys])  # key == "frame_{idx}"

    return offset


def getFrameNumber(frameKey):
    return int(frameKey.split("_")[-1])


def getVideoMarks(videoPath, marksPath):
    try:
        marks = json.load(open(marksPath, "r"))
    except:
        print(f"{Fore.RED}\nThere is no json file {marksPath} for {videoPath} {Style.RESET_ALL}")
        return {}

    marksSeparated = {}
    for frame, frameMarks in marks.items():
        subcategory = frameMarks[const.subcategory]
        coords = frameMarks[const.coords]

        putNested(dictionary=marksSeparated, keys=[subcategory, frame], value=coords)

    return marksSeparated


def summarizeInfo(rawPath=Path.raw, summarizedPath=Path.summarizedRaw, allowedSubCtgList=None,
                  overwrite=True):

    summarized = openJsonSafely(summarizedPath) if not overwrite else {}

    rawVideosPath = os.path.join(rawPath, const.videos)
    rawJsonsPath = os.path.join(rawPath, const.json)

    rawVideos = sorted([j for j in os.listdir(rawVideosPath) if j.endswith(Extensions.videos())])

    maxIdx = summarized.get(const.maxIdx, 0)
    for i, video in enumerate(rawVideos):
        print(f"\rProcessing {video} ({i + 1} out of {len(rawVideos)})", end="")

        category, name = extractCategory(video)
        categoryInfo = summarized.get(category, {})

        videoJson = os.path.join(rawJsonsPath, makeJSONname(name))
        videoMarks = getVideoMarks(os.path.join(rawVideosPath, video), videoJson)

        for subctg, subctgMarks in videoMarks.items():
            if allowedSubCtgList is not None and subctg not in allowedSubCtgList:
                continue

            if subctg not in categoryInfo:
                subctgIdx = maxIdx
                maxIdx += 1

                curSubctgMarks = {
                    const.overall: 0,
                    const.ctgIdx: subctgIdx,
                    const.videos: {},
                    const.parent: category
                }
            else:
                curSubctgMarks = categoryInfo[subctg]

            if video not in curSubctgMarks[const.videos]:
                curSubctgMarks[const.videos][video] = subctgMarks
                curSubctgMarks[const.overall] += len(subctgMarks)

            categoryInfo[subctg] = curSubctgMarks

        if categoryInfo:
            summarized[category] = categoryInfo
            summarized[const.maxIdx] = maxIdx

    json.dump(summarized, open(summarizedPath, "w"), indent=3)
    print(f"\n{Fore.GREEN}Summarized info file {summarizedPath} has been updated{Style.RESET_ALL}")


def fixFrameNumbers(jsonPath):
    jsons = [j for j in os.listdir(jsonPath) if j.endswith(Extensions.json)]

    for js in jsons:
        path = os.path.join(jsonPath, js)
        marks = openJsonSafely(path)

        if not marks:
            continue

        offset = getKeysOffset(marks.keys())

        if offset == 0:
            continue

        fixedMarks = {}
        for frame, info in marks.items():
            newFrame = "frame_{}".format(getFrameNumber(frame) - offset)
            fixedMarks[newFrame] = info

        json.dump(fixedMarks, open(path, "w"), indent=3)
        print(f"{Fore.BLUE}JSON file {path} has been fixed{Style.RESET_ALL}")


def main():
    from config import Sets
    summarizeInfo(allowedSubCtgList=Sets.subcategories)


if __name__ == "__main__":
    main()
