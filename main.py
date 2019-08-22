import shutil
import os
import json

import cv2
import numpy as np

from random import shuffle, seed

categoryPrev = {
   "astronomiya-2009": 0,
   "bandikut-2011": 1,
   "bashnya-2010": 2,
   "belyye-nochi-2013": 3,
   "dumskaya-bashnya-2010": 4,
   "kavaleriya-1812-2012": 5,
   "klyuch-k-serdtsu-2017": 6,
   "koala-s-opala-2012": 7,
   "koleso-fortuny-2018": 8,
   "lastochkino-gnezdo-2012": 9,
   "livadiyskiy-dvorets-2013": 10,
   "london-2014": 11,
   "lyubov-dragotsenna-2018": 12,
   "matrona-moskvina-2017": 13,
   "moskva-2014": 14,
   "Osminog-2012": 15,
   "pauk-2011": 16,
   "serafim-svarovskiy-2018": 17,
   "sergiy-radonezhskiy-2018": 18,
   "simvoli-rossii-kiji-2015": 19,
   "strelets-2014": 20,
   "svinya-s-babochkoy-2019": 21,
   "tigr-II-2011": 22,
   "viktor-tsoy-2012": 23,
   "yaytso-moskovskiy-kreml-2013": 24,
   "yekaterininskiy-dvorets-2010": 25,
   "Akhaltekinskiy-kon-2011-avers": 26,
   "Akhaltekinskiy-kon-2011-reverse": 27,
   "Bayk-2007-avers": 28,
   "Bayk-2007-reverse": 29,
   "Bekenbaue-2012-reverse": 30,
   "BELYY-MEDVED-2012-avers": 31,
   "BELYY-MEDVED-2012-reverse": 32,
   "buki-2013-avers": 33,
   "Bychek-2009-avers": 34,
   "Bychek-2009-reverse": 35,
   "Dinozavry-morskiye-2013-avers": 36,
   "Dinozavry-morskiye-2013-reverse": 37,
   "Dzhaz-2010-avers": 38,
   "Dzhaz-2010-reverse": 39,
   "KHRAM-KHRISTA-SPASITELYA-2012-v-avers": 40,
   "KHRAM-KHRISTA-SPASITELYA-2012-v-reverse": 41,
   "KITAYSKAYA-KHOKHLATAYA-2012-avers": 42,
   "KITAYSKAYA-KHOKHLATAYA-2012-reverse": 43,
   "krylataya-loshad-2014-avers": 44,
   "krylataya-loshad-2014-reverse": 45,
   "More-lyubvi-2017-avers": 46,
   "More-lyubvi-2017-reverse": 47,
   "Noterdam-2010-avers": 48,
   "Noterdam-2010-reverse": 49,
   "Panda-2013-avers": 50,
   "Panda-2013-reverse": 51,
   "Parizh-2013-avers": 52,
   "Parizh-2013-reverse": 53,
   "Pele-2008-avers": 54,
   "Pele-2008-reverse": 55,
   "Pervyy-samolet-2011-avers": 56,
   "Pervyy-samolet-2011-reverse": 57,
   "Polet-k-zvezdam-2012-avers": 58,
   "Polet-k-zvezdam-2012-reverse": 59,
   "renuar-2008S-avers": 60,
   "renuar-2008S-reverse": 61,
   "Russkaya-golubaya-2019-avers": 62,
   "Russkaya-golubaya-2019-reverse": 63,
   "Ryby-2011-avers": 64,
   "Ryby-2011-reverse": 65,
   "Snegovik-2009-avers": 66,
   "Snegovik-2009-reverse": 67,
   "Telets-2009-avers": 68,
   "Telets-2009-reverse": 69,
   "Tigrenok-2010-avers": 70,
   "Tigrenok-2010-reverse": 71,
   "Tigrnok-2010-avers": 72,
   "Tigrnok-2010-reverse": 73
}

category = {
    "astronomiya-2009": 0,
   "bandikut-2011": 1,
   "bashnya-2010": 2,
   "dumskaya-bashnya-2010": 3,
   "kavaleriya-1812-2012": 4,
   "klyuch-k-serdtsu-2017": 5,
   "koala-s-opala-2012": 6,
   "koleso-fortuny-2018": 7,
   "lastochkino-gnezdo-2012": 8,
   "livadiyskiy-dvorets-2013": 9,
   "london-2014": 10,
   "lyubov-dragotsenna-2018": 11,
   "matrona-moskvina-2017": 12,
   "moskva-2014": 13,
   "Osminog-2012": 14,
   "pauk-2011": 15,
   "serafim-svarovskiy-2018": 16,
   "sergiy-radonezhskiy-2018": 17,
   "simvoli-rossii-kiji-2015": 18,
   "strelets-2014": 19,
   "svinya-s-babochkoy-2019": 20,
   "tigr-II-2011": 21,
   "viktor-tsoy-2012": 22,
   "yekaterininskiy-dvorets-2010": 23,
   "Akhaltekinskiy-kon-2011-avers": 24,
   "Akhaltekinskiy-kon-2011-reverse": 25,
   "Bayk-2007-avers": 26,
   "Bayk-2007-reverse": 27,
   "Bekenbaue-2012-reverse": 28,
   "BELYY-MEDVED-2012-avers": 29,
   "BELYY-MEDVED-2012-reverse": 30,
   "buki-2013-avers": 31,
   "Bychek-2009-avers": 32,
   "Bychek-2009-reverse": 33,
   "Dinozavry-morskiye-2013-avers": 34,
   "Dinozavry-morskiye-2013-reverse": 35,
   "Dzhaz-2010-avers": 36,
   "Dzhaz-2010-reverse": 37,
   "KHRAM-KHRISTA-SPASITELYA-2012-v-avers": 38,
   "KHRAM-KHRISTA-SPASITELYA-2012-v-reverse": 39,
   "KITAYSKAYA-KHOKHLATAYA-2012-avers": 40,
   "KITAYSKAYA-KHOKHLATAYA-2012-reverse": 41,
   "krylataya-loshad-2014-avers": 42,
   "krylataya-loshad-2014-reverse": 43,
   "More-lyubvi-2017-avers": 44,
   "More-lyubvi-2017-reverse": 45,
   "Noterdam-2010-avers": 46,
   "Noterdam-2010-reverse": 47,
   "Panda-2013-avers": 48,
   "Panda-2013-reverse": 49,
   "Parizh-2013-avers": 50,
   "Parizh-2013-reverse": 51,
   "Pele-2008-avers": 52,
   "Pele-2008-reverse": 53,
   "Pervyy-samolet-2011-avers": 54,
   "Pervyy-samolet-2011-reverse": 55,
   "Polet-k-zvezdam-2012-avers": 56,
   "Polet-k-zvezdam-2012-reverse": 57,
   "renuar-2008S-avers": 58,
   "renuar-2008S-reverse": 59,
   "Russkaya-golubaya-2019-avers": 60,
   "Russkaya-golubaya-2019-reverse": 61,
   "Ryby-2011-avers": 62,
   "Ryby-2011-reverse": 63,
   "Snegovik-2009-avers": 64,
   "Snegovik-2009-reverse": 65,
   "Telets-2009-avers": 66,
   "Telets-2009-reverse": 67,
   "Tigrenok-2010-avers": 68,
   "Tigrenok-2010-reverse": 69,
   "Tigrnok-2010-avers": 70,
   "Tigrnok-2010-reverse": 71
}
categoryNames = {
    "astronomiya-2009" : "astronomiya-2009",
    "bandikut-2011" : "bandikut-2011",
    "bashnya-2010" : "bashnya-2010",
    "dumskaya-bashnya-2010" : "dumskaya-bashnya-2010",
    "kavaleriya-1812-2012" : "kavaleriya-1812-2012",
    "klyuch-k-serdtsu-2017" : "klyuch-k-serdtsu-2017",
    "koala-s-opala-2012" : "koala-s-opala-2012",
    "koleso-fortuny-2018" : "koleso-fortuny-2018",
    "lastochkino-gnezdo-2012" : "lastochkino-gnezdo-2012",
    "livadiyskiy-dvorets-2013" : "livadiyskiy-dvorets-2013",
    "london-2014" : "london-2014",
    "lyubov-dragotsenna-2018" : "lyubov-dragotsenna-2018",
    "matrona-moskvina-2017" : "matrona-moskvina-2017",
    "moskva-2014" : "moskva-2014",
    "Osminog-2012" : "Osminog-2012",
    "pauk-2011" : "pauk-2011",
    "serafim-svarovskiy-2018" : "serafim-svarovskiy-2018",
    "sergiy-radonezhskiy-2018" : "sergiy-radonezhskiy-2018",
    "simvoli-rossii-kiji-2015" : "simvoli-rossii-kiji-2015",
    "strelets-2014" : "strelets-2014",
    "svinya-s-babochkoy-2019" : "svinya-s-babochkoy-2019",
    "tigr-II-2011" : "tigr-II-2011",
    "viktor-tsoy-2012" : "viktor-tsoy-2012",
    "yekaterininskiy-dvorets-2010" : "yekaterininskiy-dvorets-2010",
    "Akhaltekinskiy-kon-2011-avers" : "Akhaltekinskiy-kon-2011-avers",
    "Akhaltekinskiy-kon-2011-reverse" : "Akhaltekinskiy-kon-2011-reverse",
    "Bayk-2007-avers" : "Bayk-2007-avers",
    "Bayk-2007-reverse" : "Bayk-2007-reverse",
    "Bekenbaue-2012-reverse" : "Bekenbaue-2012-reverse",
    "BELYY-MEDVED-2012-avers" : "BELYY-MEDVED-2012-avers",
    "BELYY-MEDVED-2012-reverse" : "BELYY-MEDVED-2012-reverse",
    "buki-2013-avers" : "buki-2013-avers",
    "Bychek-2009-avers" : "Bychek-2009-avers",
    "Bychek-2009-reverse" : "Bychek-2009-reverse",
    "Dinozavry-morskiye-2013-avers" : "Dinozavry-morskiye-2013-avers",
    "Dinozavry-morskiye-2013-reverse" : "Dinozavry-morskiye-2013-reverse",
    "Dzhaz-2010-avers" : "Dzhaz-2010-avers",
    "Dzhaz-2010-reverse" : "Dzhaz-2010-reverse",
    "KHRAM-KHRISTA-SPASITELYA-2012-v-avers" : "KHRAM-KHRISTA-SPASITELYA-2012-v-avers",
    "KHRAM-KHRISTA-SPASITELYA-2012-v-reverse" : "KHRAM-KHRISTA-SPASITELYA-2012-v-reverse",
    "KITAYSKAYA-KHOKHLATAYA-2012-avers" : "KITAYSKAYA-KHOKHLATAYA-2012-avers",
    "KITAYSKAYA-KHOKHLATAYA-2012-reverse" : "KITAYSKAYA-KHOKHLATAYA-2012-reverse",
    "krylataya-loshad-2014-avers" : "krylataya-loshad-2014-avers",
    "krylataya-loshad-2014-reverse" : "krylataya-loshad-2014-reverse",
    "More-lyubvi-2017-avers" : "More-lyubvi-2017-avers",
    "More-lyubvi-2017-reverse" : "More-lyubvi-2017-reverse",
    "Noterdam-2010-avers" : "Noterdam-2010-avers",
    "Noterdam-2010-reverse" : "Noterdam-2010-reverse",
    "Panda-2013-avers" : "Panda-2013-avers",
    "Panda-2013-reverse" : "Panda-2013-reverse",
    "Parizh-2013-avers" : "Parizh-2013-avers",
    "Parizh-2013-reverse" : "Parizh-2013-reverse",
    "Pele-2008-avers" : "Pele-2008-avers",
    "Pele-2008-reverse" : "Pele-2008-reverse",
    "Pervyy-samolet-2011-avers" : "Pervyy-samolet-2011-avers",
    "Pervyy-samolet-2011-reverse" : "Pervyy-samolet-2011-reverse",
    "Polet-k-zvezdam-2012-avers" : "Polet-k-zvezdam-2012-avers",
    "Polet-k-zvezdam-2012-reverse" : "Polet-k-zvezdam-2012-reverse",
    "renuar-2008S-avers" : "renuar-2008S-avers",
    "renuar-2008S-reverse" : "renuar-2008S-reverse",
    "Russkaya-golubaya-2019-avers" : "Russkaya-golubaya-2019-avers",
    "Russkaya-golubaya-2019-reverse" : "Russkaya-golubaya-2019-reverse",
    "Ryby-2011-avers" : "Ryby-2011-avers",
    "Ryby-2011-reverse" : "Ryby-2011-reverse",
    "Snegovik-2009-avers" : "Snegovik-2009-avers",
    "Snegovik-2009-reverse" : "Snegovik-2009-reverse",
    "Telets-2009-avers" : "Telets-2009-avers",
    "Telets-2009-reverse" : "Telets-2009-reverse",
    "Tigrenok-2010-avers" : "Tigrenok-2010-avers",
    "Tigrenok-2010-reverse" : "Tigrenok-2010-reverse",
    "Tigrnok-2010-avers" : "Tigrnok-2010-avers",
    "Tigrnok-2010-reverse" : "Tigrnok-2010-reverse"
}
categoryNamesPrev = {
    "astronomiya-2009" : "astronomiya-2009",
    "bandikut-2011" : "bandikut-2011",
    "bashnya-2010" : "bashnya-2010",
    "belyye-nochi-2013" : "belyye-nochi-2013",
    "dumskaya-bashnya-2010" : "dumskaya-bashnya-2010",
    "kavaleriya-1812-2012" : "kavaleriya-1812-2012",
    "klyuch-k-serdtsu-2017" : "klyuch-k-serdtsu-2017",
    "koala-s-opala-2012" : "koala-s-opala-2012",
    "koleso-fortuny-2018" : "koleso-fortuny-2018",
    "lastochkino-gnezdo-2012" : "lastochkino-gnezdo-2012",
    "livadiyskiy-dvorets-2013" : "livadiyskiy-dvorets-2013",
    "london-2014" : "london-2014",
    "lyubov-dragotsenna-2018" : "lyubov-dragotsenna-2018",
    "matrona-moskvina-2017" : "matrona-moskvina-2017",
    "moskva-2014" : "moskva-2014",
    "Osminog-2012" : "Osminog-2012",
    "pauk-2011" : "pauk-2011",
    "serafim-svarovskiy-2018" : "serafim-svarovskiy-2018",
    "sergiy-radonezhskiy-2018" : "sergiy-radonezhskiy-2018",
    "simvoli-rossii-kiji-2015" : "simvoli-rossii-kiji-2015",
    "strelets-2014" : "strelets-2014",
    "svinya-s-babochkoy-2019" : "svinya-s-babochkoy-2019",
    "tigr-II-2011" : "tigr-II-2011",
    "viktor-tsoy-2012" : "viktor-tsoy-2012",
    "yaytso-moskovskiy-kreml-2013" : "yaytso-moskovskiy-kreml-2013",
    "yekaterininskiy-dvorets-2010" : "yekaterininskiy-dvorets-2010",
    "Akhaltekinskiy-kon-2011-avers" : "Akhaltekinskiy-kon-2011-avers",
    "Akhaltekinskiy-kon-2011-reverse" : "Akhaltekinskiy-kon-2011-reverse",
    "Bayk-2007-avers" : "Bayk-2007-avers",
    "Bayk-2007-reverse" : "Bayk-2007-reverse",
    "Bekenbaue-2012-reverse" : "Bekenbaue-2012-reverse",
    "BELYY-MEDVED-2012-avers" : "BELYY-MEDVED-2012-avers",
    "BELYY-MEDVED-2012-reverse" : "BELYY-MEDVED-2012-reverse",
    "buki-2013-avers" : "buki-2013-avers",
    "Bychek-2009-avers" : "Bychek-2009-avers",
    "Bychek-2009-reverse" : "Bychek-2009-reverse",
    "Dinozavry-morskiye-2013-avers" : "Dinozavry-morskiye-2013-avers",
    "Dinozavry-morskiye-2013-reverse" : "Dinozavry-morskiye-2013-reverse",
    "Dzhaz-2010-avers" : "Dzhaz-2010-avers",
    "Dzhaz-2010-reverse" : "Dzhaz-2010-reverse",
    "KHRAM-KHRISTA-SPASITELYA-2012-v-avers" : "KHRAM-KHRISTA-SPASITELYA-2012-v-avers",
    "KHRAM-KHRISTA-SPASITELYA-2012-v-reverse" : "KHRAM-KHRISTA-SPASITELYA-2012-v-reverse",
    "KITAYSKAYA-KHOKHLATAYA-2012-avers" : "KITAYSKAYA-KHOKHLATAYA-2012-avers",
    "KITAYSKAYA-KHOKHLATAYA-2012-reverse" : "KITAYSKAYA-KHOKHLATAYA-2012-reverse",
    "krylataya-loshad-2014-avers" : "krylataya-loshad-2014-avers",
    "krylataya-loshad-2014-reverse" : "krylataya-loshad-2014-reverse",
    "More-lyubvi-2017-avers" : "More-lyubvi-2017-avers",
    "More-lyubvi-2017-reverse" : "More-lyubvi-2017-reverse",
    "Noterdam-2010-avers" : "Noterdam-2010-avers",
    "Noterdam-2010-reverse" : "Noterdam-2010-reverse",
    "Panda-2013-avers" : "Panda-2013-avers",
    "Panda-2013-reverse" : "Panda-2013-reverse",
    "Parizh-2013-avers" : "Parizh-2013-avers",
    "Parizh-2013-reverse" : "Parizh-2013-reverse",
    "Pele-2008-avers" : "Pele-2008-avers",
    "Pele-2008-reverse" : "Pele-2008-reverse",
    "Pervyy-samolet-2011-avers" : "Pervyy-samolet-2011-avers",
    "Pervyy-samolet-2011-reverse" : "Pervyy-samolet-2011-reverse",
    "Polet-k-zvezdam-2012-avers" : "Polet-k-zvezdam-2012-avers",
    "Polet-k-zvezdam-2012-reverse" : "Polet-k-zvezdam-2012-reverse",
    "renuar-2008S-avers" : "renuar-2008S-avers",
    "renuar-2008S-reverse" : "renuar-2008S-reverse",
    "Russkaya-golubaya-2019-avers" : "Russkaya-golubaya-2019-avers",
    "Russkaya-golubaya-2019-reverse" : "Russkaya-golubaya-2019-reverse",
    "Ryby-2011-avers" : "Ryby-2011-avers",
    "Ryby-2011-reverse" : "Ryby-2011-reverse",
    "Snegovik-2009-avers" : "Snegovik-2009-avers",
    "Snegovik-2009-reverse" : "Snegovik-2009-reverse",
    "Telets-2009-avers" : "Telets-2009-avers",
    "Telets-2009-reverse" : "Telets-2009-reverse",
    "Tigrenok-2010-avers" : "Tigrenok-2010-avers",
    "Tigrenok-2010-reverse" : "Tigrenok-2010-reverse",
    "Tigrnok-2010-avers" : "Tigrnok-2010-avers",
    "Tigrnok-2010-reverse" : "Tigrnok-2010-reverse",
}


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


def prepareAll(picturesFolder, idx):
    picturesDet = []
    picturesCls = []

    marks = json.load(open(os.path.join(picturesFolder, "mark.json"), "r"))
    pictures = [os.path.join(picturesFolder, name) for name in os.listdir(picturesFolder) if name.endswith(".jpg")]

    # classifierPicturesFolder = os.path.join(picturesFolder, "cut")
    # if os.path.exists(classifierPicturesFolder):
        #shutil.rmtree(classifierPicturesFolder)

    #os.makedirs(classifierPicturesFolder, exist_ok=True)

    detectorFiles = []
    classifierFiles = []

    for i, imagePath in enumerate(pictures):
        i += idx
        #imageName os.path.basename(imagePath)

        if not imagePath in marks or not marks[imagePath]:
            continue

        categoryName = marks[imagePath]["category"]

        if categoryPrev[categoryName] == category[categoryName]:
            print(f"Add to trainD.txt {imagePath}")
            detectorFiles.append(imagePath)
            continue

        print(f"Create .txt for {imagePath}")
        y1, x1, y2, x2 = marks[imagePath]["coords"]
        categoryIdx = category[categoryName]

        image = cv2.imread(imagePath, 1)
        height, width = image.shape[:2]
        detectorFiles.append(imagePath)

        y1 = max(0, y1)
        y2 = min(height, y2)
        x1 = max(0, x1)
        x2 = min(width, x2)

        bbox = image[y1 + 10:y2 - 10, x1 - 10:x2 + 10, :]

        yc = ((y2 + y1) // 2) / height
        xc = ((x2 + x1) // 2) / width
        h = (y2 - y1) / height
        w = (x2 - x1) / width

        imageString = f"{categoryIdx} {xc} {yc} {w} {h}\n"

        with open(imagePath.replace(".jpg", ".txt"), "w") as file:
            file.write(imageString)

        fnameNew = categoryNames[categoryName]
        fnameNew = fnameNew.replace("_", "-")
        # fnameNew = imageName.split("_")[:-2]
        # fnameNew = " ".join(fnameNew)
        newName = f"{i}_{fnameNew}.jpg"

        # if not os.path.exists(os.path.join(classifierPicturesFolder, newName)):
        #     cv2.imwrite(os.path.join(classifierPicturesFolder, newName), bbox)

        #classifierFiles.append(os.path.join(classifierPicturesFolder, newName))

    picturesDet.extend(permutate([name + "\n" for name in detectorFiles]))
    # picturesCls.extend(permutate([name + "\n" for name in classifierFiles]))

    picturesDet = permutate(picturesDet)
    # picturesCls = permutate(picturesCls)

    return picturesDet, picturesCls

#
# def prepareClassifierFiles(cdir, idx):
#     for i in range(1, 4):
#         flist = []
#         os.makedirs(os.path.join(cdir, "renamed"), exist_ok=True)
#
#         jsonPath = os.path.join(cdir, "mark.json")
#         cdir = os.path.join(cdir, "picrures")
#         pictures = [name for name in os.listdir(cdir) if os.path.isfile(os.path.join(cdir, name))]
#
#         marks = json.load(open(jsonPath, "r"))
#
#         for i, fname in enumerate(pictures):
#             imageMarks = marks.pop(fname, None)
#
#             i += (idx + 1)
#             fnameNew = fname.split("_")[:-1]
#             fnameNew = "-".join(fnameNew)
#
#             newName = f"{i}_{fnameNew}.png"
#
#             newPath = os.path.join(cdir, "renamed", newName)
#             flist.append(newPath + '\n')
#
#             imageMarks[newName] = imageMarks
#
#             if not os.path.exists(newPath):
#                 shutil.copy2(os.path.join(cdir, fname), newPath)
#
#     return permutate(flist), idx + i


# def createLabels(trainFile, json_):
#     marks = json.load(open(json_, "r"))
#
#     with open(trainFile, "r") as file:
#         filePaths = [path.strip() for path in file.readlines()]
#
#     for file in filePaths:
#         name = os.path.basename(file)
#
#         imageMarks = marks.get(name, None)
#         if imageMarks:
#             clsName = imageMarks["name"]
#             coords = imageMarks["coords"]
#             clsIdx = category[clsName.replace("_", "-")]
#
#             image = cv2.imread(file)
#             if image is None:
#                 continue

def main():
    rootDir = r'C:\Projects\data\coins'
    rootDir = r'E:\data\coins\sber'
    frameDir = r'E:\data\coins\frames' # os.path.join(rootDir, frames)
    videoDir = os.path.join(rootDir, 'video')

    fileListD = []
    fileListC = []

    idx = 0

    for cdir in os.listdir(frameDir):
        videoPath = os.path.join(videoDir, f"{cdir}.MOV")
        if os.path.exists(videoPath):
            curDetList, curCategoryList = prepareAll(os.path.join(frameDir, cdir), idx)
            idx += len(curCategoryList) + 1
            # fileListC.extend(curCategoryList)
            fileListD.extend(curDetList)

    # C:\\Projects\\coins\\data\\coins\\frames\\imgs\
    # frameRublesDir = r"C:\Projects\coins\data\coins\frames\imgs"
    # for cdir in os.listdir(frameRublesDir):
    #     curDetList, curCategoryList = prepareAll(os.path.join(frameRublesDir, cdir), idx)
    #     idx += len(curCategoryList) + 1
    #     fileListC.extend(curCategoryList)
    #
    #     fileListD.extend(curDetList)

    # fileListC = permutate(fileListC)
    fileListD = permutate(fileListD)

    # with open("trainC.txt", "w") as file:
    #     file.writelines(fileListC)

    with open("trainD.txt", "w") as file:
        file.writelines(fileListD)


if __name__ == '__main__':
    main()
