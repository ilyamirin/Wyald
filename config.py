import os


class Extensions:
    json = ".json"
    xml = ".xml"
    txt = ".txt"
    mov = ".mov"
    mp4 = ".mp4"
    jpg = ".jpg"
    png = ".png"
    jpeg = ".jpeg"
    list_ = ".list"
    names = ".names"


    @staticmethod
    def images():
        baseExtensions = [Extensions.jpg, Extensions.png, Extensions.jpeg]
        return baseExtensions + [i.upper() for i in baseExtensions]


    @staticmethod
    def videos():
        baseExtensions = [Extensions.mov, Extensions.mp4]
        return baseExtensions + [i.upper() for i in baseExtensions]


class Constants:
    separator = "-"
    dataset = "dataset"

    frames = "frames"
    cut = "cut"
    sets = "sets"
    raw = "raw_data"
    marks = "marks"
    videos = "videos"
    json = "json"
    xml = "xml"

    actualInfo = "actual_info"
    processedFiles = "processed_files"
    categories = "categories"
    fullCategories = "fullCategories"

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
    root = r"D:\projects\coins\test_data"

    actualInfo = os.path.join(root, f"{Constants.actualInfo}{Extensions.json}")
    processedFiles = os.path.join(root, f"{Constants.processedFiles}{Extensions.list_}")

    categories = os.path.join(root, f"{Constants.categories}{Extensions.names}")
    fullCategories = os.path.join(root, f"{Constants.fullCategories}{Extensions.names}")

    sets = os.path.join(root, Constants.sets)

    dataset = os.path.join(root, Constants.dataset)
    rawVideos = os.path.join(root, Constants.raw, Constants.videos)
    rawJson = os.path.join(root, Constants.raw, Constants.json)
    rawXml = os.path.join(root, Constants.raw, Constants.xml)