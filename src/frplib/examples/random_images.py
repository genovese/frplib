# Random Image Example in Chapter 0 Section 2.3

import PIL
from PIL import Image as PillowImage
from PIL import ImageOps, ImageShow


__all__ = [
    'random_image', 'ImageModels', 'show_image',
    'empty_image', 'pixel0', 'pixel1', 'as_image', 'add_image',
    'clockwise', 'counter_clockwise', 'reflect_image_horizontally',
    'reflect_image_vertically', 'invert_image',
    'black_pixels', 'white_pixels', 'crop', 'expand',
    'largest_cluster_size', # median_smooth, conway,
    'erode', 'dilate',
    'image_distance', 'closest_image_to',
    'reconstruct_image', 'max_likelihood_image', 'simulate_denoise',
]

import math

from collections.abc     import Iterable
from itertools           import chain, repeat
from random              import randrange
from typing              import cast, Literal, Union
from typing_extensions   import TypeAlias, Unpack

from frplib.exceptions   import IndexingError, OperationError
from frplib.frps         import FRP, frp
from frplib.kinds        import weighted_as
from frplib.quantity     import as_quantity
from frplib.statistics   import Statistic, statistic, Fork, Id
from frplib.utils        import irange
from frplib.vec_tuples   import VecTuple, as_vec_tuple, vec_tuple

ImageData: TypeAlias = tuple[Literal[0, 1], ...]
Image: TypeAlias = tuple[int, int, Unpack[ImageData]]
ImageId: TypeAlias = Union[str, int]
ModelId: TypeAlias = Union[str, int]

#
# Basic Image Components
#

def empty_image(width=32, height=32):
    "Returns an empty width x height image as a value."
    n = width * height
    return as_vec_tuple([width, height] + [0] * n)

pixel0 = (0,)  # These can be combined with as_image as in the text
pixel1 = (1,)


#
# Creating Images
#

def as_image(pixels: Iterable[Literal[0, 1]], width=32, height=32) -> Image:
    # ATTN: check for array structure, pad to proper length, etc
    return cast(Image, vec_tuple(width, height, *pixels))


#
# Helpers
#

def conform_image(image: Image, width=32, height=32) -> Image:
    "ATTN"
    wd, ht = image[:2]

    # Optimize for the most common case at the cost of an extra comparison
    if wd == width and ht == height:
        return image

    data: ImageData = image[2:]   # type: ignore

    if wd == width:
        if ht > height:
            return as_image(data, width, height)
        return as_image(chain(data, repeat(0, width * (height - ht))), width, height)

    n = width * height
    conf: list[Literal[0, 1]] = [0] * n

    if wd < width:
        for i in range(min(ht, height)):
            conf[(i * width):(i * width + wd)] = data[(i * wd):((i + 1) * wd)]
    else:
        for i in range(min(ht, height)):
            conf[(i * width):((i + 1) * width)] = data[(i * wd):(i * wd + width)]

    return as_image(conf, width, height)

def ensure_same_dims(image1: Image, image2: Image) -> tuple[int, int]:
    "Ensures that two images have the same dimensions."
    wd1, ht1 = image1[:2]
    wd2, ht2 = image2[:2]

    if wd1 != wd2:
        raise OperationError(f'Attempt to add images of different widths {wd1} != {wd2}')

    if ht1 != ht2:
        raise OperationError(f'Attempt to add images of different heights {ht1} != {ht2}')

    return (wd1, ht1)

def image_data(image: Image) -> tuple[int, int, ImageData]:
    "Decomposes an encoded image into dimensions and binary image data."
    wd, ht = image[:2]
    data = cast(ImageData, image[2:])
    return (wd, ht, data)

def add_base(base: Image):
    ""
    wd, ht = base[:2]
    n = wd * ht

    @statistic
    def do_add(img):
        # ensure_same_dims(img, base)  # conform image to base here but for now...
        new_img = cast(VecTuple, conform_image(img, wd, ht))
        return as_image((new_img[2 + i] ^ base[2 + i] for i in range(n)), wd, ht)

    return do_add

#
# Manipulating Images
#

def add_image(image1: Image, image2: Image) -> Image:
    #
    wd, ht = ensure_same_dims(image1, image2)
    n = wd * ht
    return as_image((image1[2 + i] ^ image2[2 + i] for i in range(n)), wd, ht)   # type: ignore

def clockwise(image: Image) -> Image:
    "A statistic that rotates an image 90 degrees clockwise."
    wd, ht, data = image_data(image)

    rotated: list[Literal[0, 1]] = [0] * (wd * ht)
    for j in range(ht):
        for i in range(wd):
            rotated[(ht - j - 1) + i * ht] = data[i + j * wd]

    return as_image(rotated, ht, wd)

def counter_clockwise(image: Image) -> Image:
    "A statistic that rotates an image 90 degrees counter-clockwise."
    wd, ht, data = image_data(image)

    rotated: list[Literal[0, 1]] = [0] * (wd * ht)
    for j in range(ht):
        for i in range(wd):
            rotated[j + (wd - i - 1) * ht] = data[i + j * wd]

    return as_image(rotated, wd, ht)

@statistic
def reflect_image_horizontally(image: Image) -> Image:
    "A statistic that reflects an image across its vertical midline."
    wd, ht, data = image_data(image)

    reflected: list[Literal[0, 1]] = [0] * (wd * ht)
    for j in range(ht):
        for i in range(wd):
            reflected[(wd - i - 1) + j * wd] = data[i + j * wd]

    return as_image(reflected, wd, ht)

@statistic
def reflect_image_vertically(image: Image) -> Image:
    "A statistic that reflects an image across its horizontal midline."
    wd, ht, data = image_data(image)

    reflected: list[Literal[0, 1]] = [0] * (wd * ht)
    for j in range(ht):
        for i in range(wd):
            reflected[i + (ht - j - 1) * wd] = data[i + j * wd]

    return as_image(reflected, wd, ht)

@statistic
def invert_image(image: Image) -> Image:
    "A statistic that reflects an image across its horizontal midline."
    wd, ht, data = image_data(image)

    inverted = cast(list[Literal[0, 1]], [1 - pixel for pixel in data])
    return as_image(inverted, wd, ht)

def crop(width, height, left=1, top=1):
    """A statistic factory that crops an image inside a specified frame.

    width  -- width of the cropping frame
    height -- height of the cropping frame
    left   -- leftmost column of the cropping frame;
                defaults to first column of the image
    top    -- topmost row of the cropping frame;
                defaults to first row of the image

    If the image is completely contained in the specified frame
    in one dimension, the original dimension is used.

    """
    row = top - 1
    col = left - 1

    @statistic(description=f'crops an image in a {width}x{height}+{left}+{top} frame')
    def do_crop(image: Image) -> Image:
        wd, ht, data = image_data(image)
        w = min(width, max(wd - col, 0))
        h = min(height, max(ht - row, 0))

        cropped: list[Literal[0, 1]] = [0] * (w * h)
        for i in range(h):
            for j in range(w):
                cropped[j + i * w] = data[(j + col) + (i + row) * wd]

        return as_image(cropped, w, h)

    return do_crop

def expand(horizontal: int, vertical: int):
    """A statistic factory that expands an image by a specified amount in each dimension.

    Expansion repeats each pixel the specified number of times
    in the specified direction.

    horizontal -- expansion factor across columns
    vertical   -- expansion factor across rows

    Both must be positive integers.

    """
    if horizontal <= 0 or vertical <= 0:
        raise OperationError('image expand: expansion factor must be non-negative')

    @statistic(description=f'expands an image by {horizontal} x {vertical} factors')
    def do_expand(image: Image) -> Image:
        wd, ht, data = image_data(image)

        expanded: list[Literal[0, 1]] = [0] * (wd * horizontal * ht * vertical)
        w = wd * horizontal
        h = ht * vertical
        for i in range(ht):
            for j in range(wd):
                pixel = data[j + i * wd]
                for dh in range(horizontal):
                    for dv in range(vertical):
                        expanded[dh + j * horizontal + (dv + i * vertical) * w] = pixel

        return as_image(expanded, w, h)

    return do_expand

@statistic
def largest_cluster_size(image: Image):
    "Compute the number of pixels in the largest contiguous (N-S-E-W) cluster of black pixels."
    raise OperationError('largest_cluster_size is temporarily unavailable')  # ATTN

#
# Main Image FRP Factory
#

def random_image(p='1/2', base: Union[Image, None] = None, width=None, height=None) -> FRP:
    """Returns an FRP representing a width x height random binary image.

    The image is represented as a tuple stored row-wise from the top
    left to the bottom right of the image. The width and height
    are stored as the first two components of the tuple.

    Parameters
    ----------
    p: quantity -- a value in [0__1] that specifies the Kind of the noise at
        each pixel, which equals weighted_as(0, 1, weights=[1 - p, p]).

    base: Image | None -- the image to which the noise is "added" (via
        pixelwise exclusive-or). If None, the empty image is used.

    width: int | None -- the width of the image, if supplied. If None,
        the width is taken from the base image, or 32 if no base image.

    height: int | None -- the height of the image, if supplied. If None,
        the width is taken from the base image, or 32 if no base image.

    """
    if width is None:
        width = 32 if base is None else base[0]

    if height is None:
        height = 32 if base is None else base[1]

    p = as_quantity(p)
    pixel = weighted_as(0, 1, weights=[1 - p, p])
    n = width * height

    noise: FRP = (frp(pixel) ** n) ^ Fork(width, height, Id)
    if base is None:
        return noise

    shift = add_base(conform_image(base, width, height))
    return shift(noise)


#
# Simple Image Statistics
#

@statistic
def black_pixels(image: Image):
    "Statistic that counts the number of black pixels in an image."
    _, _, data = image_data(image)
    return sum(data)

@statistic
def white_pixels(image: Image):
    "Statistic that counts the number of white pixels in an image."
    m, n, data = image_data(image)
    return m * n - sum(data)


#
# Erosion and Dilation
#

def erode(element: Union[int, Iterable[tuple[int, int]]] = 1) -> Statistic:
    """A statistic factory giving a statistic that erodes an image with the specified element.

    The element can be specified as either a positive int, creating a square
    of that size, or a sequence of integer coordinates in the element.


    """
    if isinstance(element, int):
        s = abs(element)
        delta_xl = s
        delta_xr = s
        delta_yl = s
        delta_yu = s
        element = set([(i, j) for i in irange(-s, s) for j in irange(-s, s)])
    else:
        element = set(element)
        delta_xl = max((abs(xy[0]) if xy[0] < 0 else 0) for xy in element)
        delta_xr = max((xy[0] if xy[0] > 0 else 0) for xy in element)
        delta_yl = max((abs(xy[1]) if xy[1] < 0 else 0) for xy in element)
        delta_yu = max((xy[1] if xy[1] > 0 else 0) for xy in element)

    @statistic
    def erosion(image: Image):
        wd, ht, data = image_data(image)
        width = wd - delta_xl - delta_xr
        height = ht - delta_yl - delta_yu
        eroded: list[Literal[0, 1]] = [0] * (width * height)

        for y in range(height):
            for x in range(width):
                if all(data[x + i + delta_xl + wd * (y + j + delta_yl)] == 1 for i, j in element):
                    eroded[x + width * y] = 1

        return as_image(eroded, width, height)

    return cast(Statistic, erosion)

def dilate(element: Union[int, Iterable[tuple[int, int]]] = 1) -> Statistic:
    """A statistic factory giving a statistic that dilates an image with the specified element.

    The element can be specified as either a positive int, creating a square
    of that size, or a sequence of integer coordinates in the element.

    """
    if isinstance(element, int):
        s = abs(element)
        delta_xl = s
        delta_xr = s
        delta_yl = s
        delta_yu = s
        element = set([(i, j) for i in irange(-s, s) for j in irange(-s, s)])
    else:
        element = set(element)
        delta_xl = max((abs(xy[0]) if xy[0] < 0 else 0) for xy in element)
        delta_xr = max((xy[0] if xy[0] > 0 else 0) for xy in element)
        delta_yl = max((abs(xy[1]) if xy[1] < 0 else 0) for xy in element)
        delta_yu = max((xy[1] if xy[1] > 0 else 0) for xy in element)

    @statistic
    def dilation(image):
        wd, ht, data = image_data(image)
        width = wd + delta_xl + delta_xr
        height = ht + delta_yl + delta_yu
        dilated: list[Literal[0, 1]] = [0] * (width * height)

        for y in range(ht):
            for x in range(wd):
                if data[x + y * wd] == 1:
                    for i, j in element:
                        dilated[x + i + delta_xl + width * (y + j + delta_yl)] = 1

        return as_image(dilated, width, height)

    return cast(Statistic, dilation)


#
# Image Sets
#

class ImageSet:
    """
    ATTN

    """
    def __init__(self):
        self._models: dict[ModelId, list[Image]] = {}
        self._images: dict[ImageId, Image] = {}

    def register_image(self, image_id: ImageId, image: Image) -> None:
        self._images[image_id] = image

    def register_model(self, model_id: ModelId, images: Iterable[Image]) -> None:
        self._models[model_id] = list(images)

    def images(self) -> list[ImageId]:
        return list(self._images.keys())

    def image(self, image_id: ImageId) -> Image:
        if image_id in self._images:
            return self._images[image_id]
        raise IndexingError(f'Unknown image {image_id} in image registry')

    def models(self) -> list[ModelId]:
        return list(self._models.keys())

    def model(self, model_id: ModelId) -> list[Image]:
        if model_id in self._models:
            return self._models[model_id]
        raise IndexingError(f'Unknown model {model_id} in model registry')

    def observe(self, model_id: Union[ModelId, list[Image]], p='1/8'):
        "ATTN"
        if isinstance(model_id, (str, int)):
            model = self._models[model_id]
        else:
            model = model_id

        truth = model[randrange(len(model))]  # select a base uniformly
        data = random_image(base=truth, p=as_quantity(p))

        return (data, truth)

# Predefined Images and Models

ImageModels = ImageSet()

ImageModels.register_image(
    'simple',
    as_image([1 if ((i == 0 and j == 0) or
                    (i == 31 and j == 0) or
                    (i == 0 and j == 31) or
                    (i == 31 and j == 31) or
                    (i == 15 and j == 0) or
                    (i == 17 and j == 0) or
                    (i == 15 and j == 31) or
                    (i == 17 and j == 31) or
                    (i == 0 and j == 15) or
                    (i == 0 and j == 17) or
                    (i == 31 and j == 15) or
                    (i == 31 and j == 17) or
                    (i == 4 and j == 4) or
                    (i == 28 and j == 4) or
                    (i == 4 and j == 28) or
                    (i == 28 and j == 28) or
                    (8 <= i <= 9 and 8 <= j <= 9) or
                    (23 <= i <= 24 and 8 <= j <= 9) or
                    (8 <= i <= 9 and 23 <= j <= 24) or
                    (23 <= i <= 24 and 23 <= j <= 24) or
                    (14 <= i <= 18 and 14 <= j <= 18))
              else 0 for j in range(32) for i in range(32)],
             32, 32)
)


ImageModels.register_image(
    'blocks',
    as_image([1 if ((4 <= i <= 8 and 4 <= j <= 8) or
                    (6 <= i <= 12 and 10 <= j <= 13) or
                    (18 <= i <= 24 and 18 <= j <= 24) or
                    (28 <= i <= 30 and 9 <= j <= 21) or
                    (2 <= i <= 7 and 25 <= j <= 30) or
                    (28 <= i <= 29 and 28 <= j <= 29) or
                    (25 <= i <= 26 and 28 <= j <= 29) or
                    (i == 16 and j == 9) or
                    (11 <= i <= 12 and 18 <= j <= 27) or
                    (12 <= i <= 30 and 1 <= j <= 2))
              else 0 for j in range(32) for i in range(32)],
             32, 32)
)

ImageModels.register_image(
    'squares',
    as_image([1 if ((2 <= i <= 3 and 2 <= j <= 3) or
                    (5 <= i <= 6 and 2 <= j <= 3) or
                    (2 <= i <= 3 and 5 <= j <= 6) or
                    (5 <= i <= 6 and 5 <= j <= 6) or
                    (9 <= i <= 10 and 2 <= j <= 3) or
                    (14 <= i <= 15 and 2 <= j <= 3) or
                    (17 <= i <= 19 and 2 <= j <= 4) or
                    (21 <= i <= 23 and 2 <= j <= 4) or
                    (26 <= i <= 28 and 2 <= j <= 4) or
                    (2 <= i <= 5 and 8 <= j <= 11) or
                    (8 <= i <= 11 and 8 <= j <= 11) or
                    (13 <= i <= 16 and 8 <= j <= 11) or
                    (19 <= i <= 22 and 8 <= j <= 11) or
                    (27 <= i <= 30 and 8 <= j <= 11) or
                    (8 <= i <= 11 and 13 <= j <= 16) or
                    (13 <= i <= 16 and 14 <= j <= 17) or
                    (20 <= i <= 24 and 20 <= j <= 24) or
                    (27 <= i <= 31 and 20 <= j <= 24) or
                    (14 <= i <= 19 and 27 <= j <= 32) or
                    (i == 22 and j == 27) or
                    (i == 24 and j == 27) or
                    (i == 27 and j == 27) or
                    (i == 31 and j == 27) or
                    (i == 22 and j == 29) or
                    (i == 24 and j == 29) or
                    (i == 27 and j == 29) or
                    (i == 31 and j == 29) or
                    (i == 22 and j == 32) or
                    (i == 24 and j == 32) or
                    (i == 27 and j == 32) or
                    (i == 31 and j == 32) or
                    (2 <= i <= 9 and 21 <= j <= 28))
              else 0 for j in range(32) for i in range(32)],
             32, 32)
)

ImageModels.register_image(
    'minus',
    as_image([1 if (8 <= i <= 23 and 15 <= j <= 17) else 0 for j in range(32) for i in range(32)],
             32, 32)
)

ImageModels.register_image(
    'P',
    as_image([1 if ((4 <= i <= 8 and 4 <= j <= 28) or
                    (9 <= i <= 17 and 4 <= j <= 8) or
                    (18 <= i <= 22 and 4 <= j <= 16) or
                    (9 <= i <= 17 and 12 <= j <= 16) or
                    (25 <= i <= 30 and 25 <= j <= 30))
              else 0 for j in range(32) for i in range(32)],
             32, 32)
)

ImageModels.register_image(
    'E',
    as_image([1 if ((4 <= i <= 7 and 4 <= j <= 28) or
                    (8 <= i <= 17 and 4 <= j <= 7) or
                    (8 <= i <= 17 and 15 <= j <= 17) or
                    (8 <= i <= 17 and 26 <= j <= 28))
              else 0 for j in range(32) for i in range(32)],
             32, 32)
)

ImageModels.register_image(
    'F',
    as_image([1 if ((4 <= i <= 7 and 4 <= j <= 28) or
                    (8 <= i <= 17 and 4 <= j <= 7) or
                    (8 <= i <= 17 and 15 <= j <= 17))
              else 0 for j in range(32) for i in range(32)],
             32, 32)
)

ImageModels.register_image(
    'F#',
    as_image([1 if ((16 <= i <= 28 and 16 <= j <= 112) or
                    (29 <= i <= 68 and 16 <= j <= 28) or
                    (29 <= i <= 68 and 60 <= j <= 72))
              else 0 for j in range(128) for i in range(128)],
             128, 128)
)

ImageModels.register_image(
    'H',
    as_image([1 if ((4 <= i <= 7 and 4 <= j <= 28) or
                    (8 <= i <= 17 and 15 <= j <= 17) or
                    (17 <= i <= 20 and 4 <= j <= 28))
              else 0 for j in range(32) for i in range(32)],
             32, 32)
)

ImageModels.register_image(
    'L',
    as_image([1 if ((4 <= i <= 7 and 4 <= j <= 28) or
                    (8 <= i <= 17 and 25 <= j <= 28) or
                    (25 <= i <= 30 and 5 <= j <= 10))
              else 0 for j in range(32) for i in range(32)],
             32, 32)
)

ImageModels.register_model('efh', [ImageModels.image('E'), ImageModels.image('F'), ImageModels.image('H')])

#
# Image Utilities
#

def image_distance(image1: Image, image2: Image) -> int:
    "Returns the Hamming distance between two binary images of the same dimensions."
    wd, ht = ensure_same_dims(image1, image2)
    n = wd * ht
    return sum(image1[2 + i] ^ image2[2 + i] for i in range(n))  # type: ignore

def closest_image_to(image: Image, candidates: Iterable[Image]) -> Union[Image, None]:
    best, min_dist = None, None

    for cand_img in candidates:
        dist = image_distance(image, cand_img)
        if (min_dist is None) or (dist < min_dist):   # type: ignore
            min_dist = dist
            best = cand_img

    return best


#
# Reconstruction Methods
#

def reconstruct_image(model_id, denoiser=dilate()(erode())):
    """A statistics factory for reconstructing an unknown image from noisy data.

    Parameters
    ----------
    model_id: int | str - an identifier for the model holding candidate base images
    denoiser: Statistic - a denoising statistic mapping image to image

    """
    model_images = ImageModels.model(model_id)

    @statistic
    def reconstruct(observed_image):
        denoised_image = denoiser(observed_image)
        return closest_image_to(denoised_image, model_images)

    return reconstruct

def max_likelihood_image(
        model_id: ModelId,
        return_p=False,
        delta_p=0.001,
        end_p=0.5,
        start_p=0.001
) -> Statistic:
    """ATTN

    """

    def log_like(noise, log_p, log_1_p):
        wd, ht, data = image_data(noise)
        ones = sum(data)
        return log_p * ones + log_1_p * (wd * ht - ones)

    models = cast(list[VecTuple], ImageModels.model(model_id))

    @statistic
    def ml_recon(noise_like):
        max_ll = -math.inf
        best_p = 0
        best_m = None

        p = start_p
        while p < end_p:
            log_p = math.log(p)
            log_1_p = math.log(1 - p)
            for m in models:
                ll = log_like(add_image(cast(Image, m), noise_like), log_p, log_1_p)
                if ll > max_ll:
                    max_ll = ll
                    best_p = p
                    best_m = m
            p += delta_p

        if best_m is None:
            raise OperationError('ATTN')

        if return_p:
            img = list(best_m)
            img.append(best_p)
            return VecTuple(img)
        return best_m

    return cast(Statistic, ml_recon)

#
# Reconstruction Simulator
#

def simulate_denoise(
        model_id: ModelId,
        denoiser,
        p='1/8',
        observations=10_000
):
    """Evaluates denoising statistic on repeated observations from a model.

    Parameters:
     + model_id: ModelId - identifier of pre-defined model in ImageModels
     + denoiser: Statistic - a denoising statistic mapping image to image
     + p: ScalarQ - noise prevalance (0 <= p <= 1), numeric or string
     + observations: int - number of observed images to generate

    Returns a pair of numbers giving (i) the proportion of incorrect
    reconstructions over all observations, and (ii) the average
    distance between truth and reconstruction over all observations.

    """
    prop_wrong = 0
    score = 0
    for _ in range(observations):
        data, truth = ImageModels.observe(model_id, p=p)
        reconstructed = denoiser(data)
        distance = image_distance(reconstructed.value, truth)
        score += distance
        prop_wrong += (distance > 0)  # 0 if correct, 1 if not
    return (prop_wrong / observations, score / observations)


#
# Displaying Images
#

def show_image(image_in: Union[Image, FRP], border=30, return_pil_image=False):
    """Display an image in a platform-appropriate viewer.

    The input can be an image tuple or an image FRP.
    The input is returned so that this can be used
    transparently to view and operate simultaneously,
    e.g.,

        im = show_image(random_image())

    The border argument is present to account for some
    oddness on Mac platform, where Preview shifts the
    image to obscure the top, requiring a manual zoom.
    On other platforms, this maybe unnecessary.
    Set to 0 if this is undesirable, but it seems
    to do no harm.

    Returns the original input, tuple or FRP.

    """
    if isinstance(image_in, FRP):
        image = image_in.value
    else:
        image = image_in                # type: ignore

    m, n, data = image_data(image)      # type: ignore

    # Create binary image in Pillow and set pixels
    # This is slow, but there is not an easy way
    # in pillow to set it from a tuple.
    img = PillowImage.new('1', (m, n), 1)

    pixels = img.load()
    ind = 0
    for i in range(n):
        for j in range(m):
            pixels[j, i] = 1 - data[ind]
            ind += 1

    # Put transparent border so whole image shows properly on
    # Macs Preview, which has to be manually centered for some reason.
    # For other viewers, this should do no harm. Asymmetry is irksome
    # but Preview messes up the top only.

    img_scaled = img.resize((8*m, 8*n))
    img_x = ImageOps.expand(img_scaled.convert('RGBA'),
                            border=(0, border, 0, border // 6), fill=(0, 0, 0, 0))
    ImageShow.show(img_x)

    if return_pil_image:
        return img
    return image_in


#
# Utility for making image files (not for general use)
#

def mvg_image(image: Image) -> str:
    "Returns mvg format description of an image."
    wd, ht = image[:2]
    data = cast(ImageData, image[2:])

    points = [f'push graphic-context\n  viewbox 0 0 {wd} {ht}']
    for i, px in enumerate(data):
        if px == 1:
            points.append(f'  point {i % wd},{i // wd}')
    points.append('pop graphic-context')
    return '\n'.join(points) + '\n'

def mvg_of(img: Union[Image, FRP]) -> str:
    "Returns mvg format description of image or image FRP."
    if isinstance(img, FRP):
        img = img.value      # type: ignore
    return mvg_image(img)    # type: ignore

def mvg_out(filename: str, img: Union[Image, FRP]) -> None:
    "Output image in mvg format to a specified file."
    with open(filename, 'w') as f:
        f.write(mvg_of(img))
