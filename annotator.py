class Annotation:
    txt = "txt"

    json = "json"
    xml = "xml"

    @staticmethod
    def annotationExtList():
        extentions = [Annotation.txt, Annotation.json, Annotation.xml]
        extendedExtensions = extentions + [i.upper() for i in extentions]
        return tuple(extendedExtensions)

    def __init__(self, path):
        self.path = path


class JSONAnnotation(Annotation):
    pass
#
# class YoloAnnotation(Annotation):
