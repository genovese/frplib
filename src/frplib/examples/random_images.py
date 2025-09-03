# Random Image Example in Chapter 0 Section 2.3

import PIL
from PIL import Image as PillowImage
from PIL import ImageOps, ImageShow


__all__ = [
    'random_image', 'ImageModels', 'show_image',
    'empty_image', 'pixel0', 'pixel1', 'as_image', 'add_image',
    'width_of', 'height_of', 'size_of',
    'clockwise', 'counter_clockwise', 'reflect_image_horizontally',
    'reflect_image_vertically', 'invert_image',
    'black_pixels', 'white_pixels', 'crop', 'expand',
    'image_components', 'component_count', 'get_component', 'component_sizes', 'largest_cluster_size',
    'conway', 'median_smooth',
    'atop', 'besides', 'overlay',
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
from frplib.vec_tuples   import VecTuple, as_vec_tuple, vec_tuple, join

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

pixel0: ImageData = (0,)  # These can be combined with as_image as in the text
pixel1: ImageData = (1,)


#
# Creating Images
#

def as_image(pixels: Iterable[Literal[0, 1]], width=32, height=32) -> Image:
    """Creates an image of the specified width and height from a binary sequence.

    Parameters
    ----------
    pixels: an iterable binary sequence giving the image data one row at a time,
        from the top left of the image to the bottom right.

    width: the image width in pixels, must be a positive integer

    height: the image height in pixels, must be a positive integer


    """
    # ATTN: check for array structure in input?
    if width <= 0 or height <= 0:
        raise OperationError(f'as_image requires positive width ({width}) and height ({height}).')
    image = vec_tuple(width, height, *pixels)
    n = len(image)
    # If data is of insufficient length, just pad at the end with white.
    if n < 2 + width * height:
        image = join(image, [0] * (2 + width * height - n))
    return cast(Image, image)


#
# Image Properties
#

def width_of(image: Image) -> int:
    return image[0]

def height_of(image: Image) -> int:
    return image[1]

def size_of(image: Image) -> tuple[int, int]:
    return (image[0], image[1])


#
# Helpers
#

def conform_image(image: Image, width=32, height=32) -> Image:
    """Adjusts an image to a specified size by cropping or padding as needed.

    The main use case is to ensure consistency when adding or otherwise
    operating on two images. For instance, if we are adding noise to
    a base image, we will conform the noise to the base image so that
    the noise is consistent with the base image; the rest of the
    noise is ignored.

    If the image is bigger in a dimension than the target, it is
    trimmed. If it is smaller than the target, the extra region is
    filled with white pixels.

    """
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
    "Returns a statistic that adds a given base image to its input image."
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
    """Adds two binary images by pixelwise exclusive or.

    The images are required to be the same dimension, else
    an OperationError exception is raised.

    """
    wd, ht = ensure_same_dims(image1, image2)
    n = wd * ht
    return as_image((image1[2 + i] ^ image2[2 + i] for i in range(n)), wd, ht)   # type: ignore

@statistic
def clockwise(image: Image) -> Image:
    "A statistic that rotates an image 90 degrees clockwise."
    wd, ht, data = image_data(image)

    rotated: list[Literal[0, 1]] = [0] * (wd * ht)
    for j in range(ht):
        for i in range(wd):
            rotated[(ht - j - 1) + i * ht] = data[i + j * wd]

    return as_image(rotated, ht, wd)

@statistic
def counter_clockwise(image: Image) -> Image:
    "A statistic that rotates an image 90 degrees counter-clockwise."
    wd, ht, data = image_data(image)

    rotated: list[Literal[0, 1]] = [0] * (wd * ht)
    for j in range(ht):
        for i in range(wd):
            rotated[j + (wd - i - 1) * ht] = data[i + j * wd]

    return as_image(rotated, ht, wd)

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

def image_components_maps(image: Image) -> tuple[dict[int, list[int]], dict[int, int]]:
    """Computes the connected components of an image, using black pixels and N-S-E-W neighbors.

    Returns a pair of dictionaries, the first mapping cluster number to lists of pixel indices
    and the second mapping pixel indices to cluster number.

    """
    wd, ht, data = image_data(image)

    def neighbors(ind):
        nghs = []
        if ind % wd > 0:  # not in left column
            nghs.append(ind - 1)
        if ind >= wd:     # not in first row
            nghs.append(ind - wd)
        return nghs

    # Two passes, referring to the left (W) and upper (N) neighbors of each pixel
    # to label components, possibly redundant, and then a second pass to
    # reconcile multiple labels for the component.

    # Pass 1: Assign labels and build equivalent sets
    labels1: dict[int, int] = {}
    equivs1: dict[int, set[int]] = {}
    nextlab = 1
    for pixel, pval in enumerate(data):
        if pval == 1:  # black pixel
            ns = [ng for ng in neighbors(pixel) if data[ng] == 1]
            if len(ns) == 0:
                labels1[pixel] = nextlab
                equivs1[pixel] = set([pixel])
                nextlab += 1
            elif len(ns) == 1 or (len(ns) == 2 and labels1[ns[0]] == labels1[ns[1]]):
                labels1[pixel] = labels1[ns[0]]
                equivs1[pixel] = equivs1[ns[0]]  # shared reference
                equivs1[pixel].add(pixel)
            elif ns[0] < ns[1]:  # len(labs) == 2 with unequal labels
                labels1[pixel] = labels1[ns[0]]
                equivs1[pixel] = equivs1[ns[0]]  # shared reference
                equivs1[pixel].add(pixel)
                for p in equivs1[ns[1]]:
                    equivs1[pixel].add(p)
            else:  # len(labs) == 2 with unequal labels
                labels1[pixel] = labels1[ns[1]]
                equivs1[pixel] = equivs1[ns[1]]  # shared reference
                equivs1[pixel].add(pixel)
                for p in equivs1[ns[0]]:
                    equivs1[pixel].add(p)

    # Pass 2. Reduce equivalent sets to new labels
    newlab = 1  # reserve 0 for non-cluster pixels
    clusters: dict[int, list[int]] = {}  # labels -> list of indices
    labels: dict[int, int] = {}          # index -> label
    for ind, pval in enumerate(data):
        if pval == 1 and ind not in labels:
            for equiv in equivs1[ind]:
                labels[equiv] = newlab
            clusters[newlab] = list(equivs1[ind])
            newlab += 1
    return (clusters, labels)

def image_components(image: Image) -> VecTuple:
    """Computes the image connected component using a N-E-S-W neighbor relation.

    Returns an tuple of the form

      <num_comps, comp1size, ..., compNsize, width, height, data...>

    where num_comps is the number of components, compXsize is the
    size of component X, and width, height, data is an image-like
    subtuple where data consists of component labels: 0 for no
    component and 1+ for each distinct component.

    """
    comps, labels = image_components_maps(image)
    wd, ht, data = image_data(image)
    comp_data = [len(comps.keys())]                                  # number of components
    comp_data.extend(len(comp) for comp in comps.values())           # component sizes
    comp_data.extend([wd, ht])                                       # width, height
    comp_data.extend(labels.get(ind, 0) for ind in range(len(data))) # component labels or 0

    return VecTuple(comp_data)

@statistic
def component_count(image: Image):
    "gives the number of connected components of black pixels in an image"
    count, *_rest = image_components(image)
    return count

def component_sizes(image: Image) -> list[int]:
    "Returns sorted connected component sizes"
    img_comps = image_components(image)
    if img_comps[0] > 0:
        return img_comps[1:(img_comps[0] + 1)]
    return []

def get_component(which: int) -> Statistic:
    "Statistic factory for getting a component of an image as a binary image."

    @statistic
    def component_getter(image: Image):
        "gets a selected connected component from an image"
        img_comps = image_components(image)
        wd, ht, *cdata = img_comps[(img_comps[0] + 1):]

        if img_comps[0] < which:
            return empty_image(wd, ht)
        return as_image([1 if d == which else 0 for d in cdata], width=wd, height=ht)

    return component_getter

@statistic
def largest_cluster_size(image: Image):
    "computes the number of pixels in the largest contiguous (N-S-E-W) cluster of black pixels"
    clusters, _ = image_components_maps(image)
    max_size = 0
    for cluster in clusters.values():
        if len(cluster) > max_size:
            max_size = len(cluster)
    return max_size

@statistic
def conway(image: Image):
    "executes a step in Conway's Game of Life where black pixels are alive"
    wd, ht, data = image_data(image)
    n = wd * ht

    def step(ind):
        alive = data[ind] == 1
        x, y = (ind % wd, ind // wd)
        maybe_neighbors = [(x - 1, y), (x + 1, y), (x - 1, y - 1), (x - 1, y + 1),
                           (x, y - 1), (x, y + 1), (x + 1, y - 1), (x + 1, y + 1)]

        nghs = sum(data[x + y *wd] for x, y in maybe_neighbors if x >= 0 and x < wd and y >= 0 and y < ht)
        if alive and (nghs == 2 or nghs == 3):
            return 1
        elif not alive and nghs == 3:
            return 1
        return 0

    return as_image([step(ind) for ind in range(n)], width=wd, height=ht)

def median_smooth(d: int) -> Statistic:
    """Statistic factory producing a median smoother for an image with given neighborhood size.

    ATTN

    """
    if d <= 0:
        return Id

    thresh = ((2 * d + 1) ** 2) // 2

    @statistic
    def smoother(image: Image):
        "smooths an image, using the median of original pixel with N-S-E-W neighbors at each pixel"
        wd, ht, data = image_data(image)
        n = wd * ht

        def smooth_at(ind):
            x, y = (ind % wd, ind // wd)
            maybe_local = [(x + dx, y + dy) for dx in irange(-d, d) for dy in irange(-d, d)]

            nghs = sum(data[x + y *wd] for x, y in maybe_local if x >= 0 and x < wd and y >= 0 and y < ht)
            if nghs > thresh:
                return 1
            return 0

        return as_image([smooth_at(ind) for ind in range(n)], width=wd, height=ht)

    return smoother

# @statistic
# def median_smooth(image: Image):
#     "smooths an image, using the median of original pixel with N-S-E-W neighbors at each pixel"
#     wd, ht, data = image_data(image)
#     n = wd * ht
#
#     def smooth_at(ind):
#         x, y = (ind % wd, ind // wd)
#         maybe_local = [(x - 1, y), (x + 1, y), (x, y), (x, y - 1), (x, y + 1)]
#
#         nghs = sum(data[x + y *wd] for x, y in maybe_local if x >= 0 and x < wd and y >= 0 and y < ht)
#         if nghs >= 3:
#             return 1
#         return 0
#
#     return as_image([smooth_at(ind) for ind in range(n)], width=wd, height=ht)

def atop(image1: Image, image2: Image, gap=0) -> Image:
    """Creates a new image with the first on top of the other.

    Pads out both images to the maximum width of the two.

    Parameters
    ----------
    image1 - The image to be placed on the top of the new image
    image2 - The image to be placed on the bottom of the new image
    gap [=0] - The number of rows of white placed between the
        two parts of the new image.

    Returns the resulting combined image.

    """
    wd1 = width_of(image1)
    wd2 = width_of(image2)
    if wd1 < wd2:
        imageU = conform_image(image1, width=wd2, height=height_of(image1))
        imageD = image2
    elif wd1 > wd2:
        imageU = image1
        imageU = conform_image(image2, width=wd1, height=height_of(image2))
    else:
        imageU = image1
        imageD = image2

    wdU, htU, dataU = image_data(imageU)
    wdD, htD, dataD = image_data(imageD)

    padding: list[Literal[0, 1]] = [0] * (gap * wdU)

    return as_image(list(dataU) + padding + list(dataD), width=wdU, height=htU + gap + htD)

def besides(imageL: Image, imageR: Image, gap=0) -> Image:
    """Creates a new image with the first to the left of the other.

    Pads out both images to the maximum height of the two.

    Parameters
    ----------
    image1 - The image to be placed on the left of the new image
    image2 - The image to be placed on the right of the new image
    gap [=0] - The number of columns of white placed between the
        two parts of the new image.

    Returns the resulting combined image.

    """
    return counter_clockwise(atop(clockwise(imageL), clockwise(imageR), gap))

def overlay(imageBot: Image, imageTop: Image, offset=(0, 0)) -> Image:
    """Creates a new image by placing one image over another at specified offset.

    The size of the new image encompasses both the given images.

    Parameters
    ----------
    imageBot - the image to be placed on the bottom layer
    imageTop - the overlaying image, which overwrites the bottom image where
        they intersect
    offset [= (0,0)] - the position in the bottom image at which the top-left
        pixel of the top image is placed.

    Returns the combined image, with size encompassing both given images.

    """

    def place_at(base: list[Literal[0, 1]], width: int, height: int, inserted: Image, x: int, y: int) -> None:
        # Contract: base is big enough to encompass the inserted image
        w, h, idata = image_data(inserted)

        for j in range(h):
            for i in range(w):
                base[x + i + (y + j) * width] = idata[i + j * w]


    wdB, htB = size_of(imageBot)
    wdT, htT = size_of(imageTop)
    dx, dy = offset

    # start with dx, dy >= 0
    wd = max(wdB - min(0, dx), max(0, dx) + wdT)
    ht = max(htB - min(0, dy), max(0, dy) + htT)

    base: list[Literal[0, 1]] = list(empty_image(wd, ht)[2:])
    place_at(base, wd, ht, imageBot, -min(0, dx), -min(0, dy))
    place_at(base, wd, ht, imageTop, max(0, dx), max(0, dy))

    return as_image(base, wd, ht)


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

    return erosion

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

    return dilation


#
# Image Sets
#

class ImageSet:
    """A collection of images and groups of images as models.

    This include methods for adding new images and models
    and for observing data from a specified model.

    The .images() and .models() method give lists of the
    registered images and models.

    """
    def __init__(self):
        self._models: dict[ModelId, list[Image]] = {}
        self._images: dict[ImageId, Image] = {}

    def register_image(self, image_id: ImageId, image: Image) -> None:
        "Adds a new image by name to the image collection."
        self._images[image_id] = image

    def register_model(self, model_id: ModelId, images: Iterable[Image]) -> None:
        "Adds a new model by name to the models collection, a list of images."
        self._models[model_id] = list(images)

    def images(self) -> list[ImageId]:
        "Lists the ids of the available registered images."
        return list(self._images.keys())

    def image(self, image_id: ImageId) -> Image:
        "Returns the image with the specified name, if registered."
        if image_id in self._images:
            return self._images[image_id]
        raise IndexingError(f'Unknown image {image_id} in image registry')

    def models(self) -> list[ModelId]:
        "Lists the ids of the available registered models."
        return list(self._models.keys())

    def model(self, model_id: ModelId) -> list[Image]:
        "Returns the model with the specified name, if registered."
        if model_id in self._models:
            return self._models[model_id]
        raise IndexingError(f'Unknown model {model_id} in model registry')

    def observe(self, model_id: Union[ModelId, list[Image]], p='1/8'):
        """Generate a random image according to the model and given parameters.

        Parameters
        ----------
        model_id - the name of the model to draw data from
        p [= '1/8'] - the noise parameter for the random image

        Returns the observed data and the true image for comparison in
        a 2-tuple.

        """
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

_pulsarQ = as_image(pixel0 * 2 + pixel1 * 3 + pixel0 +
                    pixel0 * 6 +
                    pixel1 + pixel0 * 4 + pixel1 +
                    pixel1 + pixel0 * 4 + pixel1 +
                    pixel1 + pixel0 * 4 + pixel1 +
                    pixel0 * 2 + pixel1 * 3 + pixel0,
                    6, 6)
_pulsarH = atop(_pulsarQ, reflect_image_vertically(_pulsarQ), gap=1)
_pulsarI = besides(_pulsarH, reflect_image_horizontally(_pulsarH), gap=1)

ImageModels.register_image(
    'pulsar',
    overlay(empty_image(33, 33), _pulsarI, offset=(10, 10))
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
            raise OperationError('No likelihood maximizer found, all likelihoods negative infinity.')

        if return_p:
            img = list(best_m)
            img.append(best_p)
            return VecTuple(img)
        return best_m

    return ml_recon

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
    img = PillowImage.new('1', (m, n), 1)

    # This is slow, but there is not an easy way
    # in pillow to set it from a tuple.
    #pixels = img.load()
    #ind = 0
    #for i in range(n):
    #    for j in range(m):
    #        pixels[j, i] = 1 - data[ind]
    #        ind += 1

    # Updated 30-Aug-2025; putdata() is more efficient
    # Note: Pillow uses 1=black, 0=white
    img.putdata(data, scale=-1, offset=1)

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
