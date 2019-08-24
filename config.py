import os


class Extensions:
    json = ".json"
    xml = ".xml"
    txt = ".txt"
    mov = ".MOV"
    jpg = ".jpg"
    png = ".png"
    jpeg = ".jpeg"


    @property
    def images(self):
        return Extensions.jpg, Extensions.png, Extensions.jpeg


class Constants:
    separator = "-"

    frames = "frames"
    sets = "sets"
    raw = "raw_data"
    marks = "marks"

    actualInfo = "actual_info"
    processedFiles = "processed_files"
    categories = "categories"

    train = "train"
    valid = "valid"
    test = "test"

    original = "original"
    augmented = "augmented"

    avers = "avers"
    revers = "revers"
    overall = "overall"
    merged = "merged"

    coords = "coordinates"
    image = "image"
    category = "category"
    subcategory = "subcategory"
    fullCategory = "fullCategory"
    ctgIdx = "index"
    imageShape = "shape"


class Path:
    project = ""

    actualInfo = os.path.join(project, f"{Constants.actualInfo}{Extensions.json}")
    processedFiles = os.path.join(project, f"{Constants.processedFiles}{Extensions.txt}")
    categories = os.path.join(project, f"{Constants.categories}{Extensions.txt}")

    sets = os.path.join(project, Constants.sets)
    frames = os.path.join(project, Constants.frames)
    raw = os.path.join(project, Constants.raw)