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
        extensions = [Extensions.jpg, Extensions.png, Extensions.jpeg]
        extendedExtensions = extensions + [i.upper() for i in extensions]
        return tuple(extendedExtensions)


    @staticmethod
    def videos():
        extensions = [Extensions.mov, Extensions.mp4]
        extendedExtensions = extensions + [i.upper() for i in extensions]
        return tuple(extendedExtensions)


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
    summarizedRaw = "summarized_raw"
    processedFiles = "processed_files"
    processedFrames = "processedFrames"
    categories = "categories"
    fullCategories = "fullCategories"
    maxIdx = "maxIdx"

    train = "train"
    valid = "valid"
    test = "test"

    original = "original"
    augmented = "augmented"

    avers = "avers"
    revers = "revers"
    overall = "overall"
    merged = "merged"
    parent = "parent"

    coords = "coordinates"
    image = "image"
    category = "category"
    subcategory = "subcategory"
    fullCategory = "fullCategory"
    ctgIdx = "categoryIndex"
    imageShape = "shape"

    default = "default"


class Path:
    root = r"D:\projects\coins\test_data"

    dataset = os.path.join(root, Constants.dataset)

    original = os.path.join(dataset, Constants.original)

    raw = os.path.join(root, Constants.raw)
    rawVideos = os.path.join(raw, Constants.videos)
    rawJson = os.path.join(raw, Constants.json)
    rawXml = os.path.join(raw, Constants.xml)

    sets = os.path.join(root, Constants.sets)

    summarizedRaw = os.path.join(root, f"{Constants.summarizedRaw}{Extensions.json}")
    actualInfo = os.path.join(root, f"{Constants.actualInfo}{Extensions.json}")
    processedFiles = os.path.join(root, f"{Constants.processedFiles}{Extensions.list_}")
    processedFrames = os.path.join(root, f"{Constants.processedFrames}{Extensions.list_}")
    categories = os.path.join(root, f"{Constants.categories}{Extensions.names}")
    fullCategories = os.path.join(root, f"{Constants.fullCategories}{Extensions.names}")





