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
    negatives = "negatives"
    raw_final = "raw_final"
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
    reverse = "reverse"
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
    all = "all"

class Annotation:
    txt = "txt"

    json = "json"
    xml = "xml"

    @staticmethod
    def annotationExtList():
        extentions = [ Annotation.txt, Annotation.json, Annotation.xml ]
        extendedExtensions = extentions + [ i.upper() for i in extentions ]
        return tuple(extendedExtensions)


class Path:
    root = r"D:\Projects\coins-project\DATASETS\final_ext1"

    dataset = os.path.join(root, Constants.dataset)

    original = os.path.join(dataset, Constants.original)

    raw = os.path.join(root, Constants.raw)
    rawVideos = os.path.join(raw, Constants.videos)
    rawJson = os.path.join(raw, Constants.json)
    rawXml = os.path.join(raw, Constants.xml)

    negative = os.path.join(root, Constants.negatives)
    raw_final = os.path.join(root, Constants.raw_final)
    sets = os.path.join(root, Constants.sets)

    summarizedRaw = os.path.join(root, f"{Constants.summarizedRaw}{Extensions.json}")
    actualInfo = os.path.join(root, f"{Constants.actualInfo}{Extensions.json}")
    processedFiles = os.path.join(root, f"{Constants.processedFiles}{Extensions.list_}")
    processedFrames = os.path.join(root, f"{Constants.processedFrames}{Extensions.list_}")
    categories = os.path.join(root, f"{Constants.categories}{Extensions.names}")
    fullCategories = os.path.join(root, f"{Constants.fullCategories}{Extensions.names}")


class Sets:
    subcategories = (Constants.avers, Constants.reverse)