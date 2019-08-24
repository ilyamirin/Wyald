class Extensions:
    json = ".json"
    mov = ".MOV"
    jpg = ".jpg"
    png = ".png"
    jpeg = ".jpeg"


    @property
    def images(self):
        return Extensions.jpg, Extensions.png, Extensions.jpeg


class Constants:
    separator = "-"
    merged = "merged"


class Path:
    project = ""