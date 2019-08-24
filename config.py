import os


class Extensions:
    json = ".json"
    xml = ".xml"
    txt = ".txt"
    mov = ".MOV"
    jpg = ".jpg"
    png = ".png"
    jpeg = ".jpeg"


    @staticmethod
    def images():
        return Extensions.jpg, Extensions.png, Extensions.jpeg


class Constants:
    separator = "-"
    dataset = "dataset"

    frames = "frames"
    sets = "sets"
    raw = "raw_data"
    marks = "marks"
    videos = "videos"
    json = "json"
    xml = "xml"

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
    ctgIdx = "categoryIndex"
    imageShape = "shape"


class Path:
    root = r"D:\Projects\coins-project\data\test_dataset"

    actualInfo = os.path.join(root, f"{Constants.actualInfo}{Extensions.json}")
    processedFiles = os.path.join(root, f"{Constants.processedFiles}{Extensions.txt}")
    categories = os.path.join(root, f"{Constants.categories}{Extensions.txt}")

    sets = os.path.join(root, Constants.sets)
    dataset = os.path.join(root, Constants.dataset)
    rawVideos = os.path.join(root, Constants.raw, Constants.videos)
    rawJson = os.path.join(root, Constants.raw, Constants.json)
    rawXml = os.path.join(root, Constants.raw, Constants.xml)