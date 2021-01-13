GIF = "image/gif"
APNG = "image/apng"
PNG = "image/png"
JPEG = "image/jpeg"
WEBP = "image/webp"
SVG = "image/svg+xml"
BMP = "image/bmp"
ICO = "image/x-icon"
TIFF = "image/tiff"

PICTURE_FORMATS = {
    GIF: [APNG],
    PNG: [WEBP],
    JPEG: [WEBP],
    WEBP: [WEBP],
    SVG: [SVG],
    BMP: [JPEG, WEBP],
    ICO: [JPEG, WEBP],
    TIFF: [JPEG, WEBP],
}
