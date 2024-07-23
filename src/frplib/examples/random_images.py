# Random Image Example in Chapter 0 Section 2.3

from collections.abc     import Iterable
from random              import randrange
from typing              import cast, Literal, Union
from typing_extensions   import TypeAlias

from frplib.frps         import FRP, frp
from frplib.kinds        import weighted_as
from frplib.quantity     import as_quantity
from frplib.statistics   import statistic, __
from frplib.vec_tuples   import as_vec_tuple, vec_tuple

Image: TypeAlias = tuple[Literal[0, 1], ...]
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
# Helpers
#

def annotate_dims(image: Image, width=32, height=32) -> Image:
    setattr(image, 'width', width)
    setattr(image, 'height', height)
    return image

def conform_image(image: Image, width=32, height=32) -> Image:
    "ATTN"
    wd = getattr(image, 'width', None)
    ht = getattr(image, 'height', None)

    if wd == width:
        if ht == height:
            return image

        if ht > height:
            cropped = image[:(wd * ht)]
            setattr(cropped, 'height', ht)
            return cropped
    # ATTN
    pass

def check_dims(image1: Image, image2: Image):
    # Error message if dims do not match
    pass

def add_base(base: Image):
    ""

    @statistic
    def do_add(img):
        check_dims(img, base)
        return img + base

#
# Main Image FRP Factory
#

## ATTN: Would like to store width and height: do it on the tuple or the FRP or both
## In the text we only use, 32 x 32 but it's worth being more general
## Try storing them in the first two components  <width, height, pixels...>

def random_image(p='1/2', base: Union[Image, None] = None, width=32, height=32) -> FRP:
    """Returns an FRP representing a width x height random binary image.

    The image is represented as a tuple stored row-wise from the top
    left to the bottom right of the image.

    ATTN

    """
    p = as_quantity(p)
    pixel = weighted_as(0, 1, weights=[1 - p, p])
    n = width * height

    @statistic
    def with_dims(img: Image) -> Image:
        return annotate_dims(img, width, height)

    noise: FRP = with_dims( frp(pixel) ** n )    # type: ignore
    if base is None:
        return noise

    # select or extend base for width and height

    return noise ^ add_base(base)


#
# Creating and Manipulating Images
#

def as_image(pixels: Iterable[Literal[0, 1]], width=32, height=32) -> Image:
    # ATTN: check for array structure, pad to proper length, etc
    return cast(Image, vec_tuple(pixels))

def add_image(image1: Image, image2: Image) -> Image:
    #
    ...

def clockwise(image: Image) -> Image:
    ...

def counter_clockwise(image: Image) -> Image:
    ...

def reflect_image(image: Image, vertical=True) -> Image:
    ...


#
# Erosion and Dilation
#



#
# Image Sets
#

class ImageSet:
    """
    ATTN

    """
    # Methods  .models, .image, .observed
    # Also add methods to add/edit models and images

    def __init__(self):
        self._models: dict[ModelId, list[Image]] = {}
        self._images: dict[ImageId, Image] = {}

    def register_image(self, image_id: str, image: Image) -> None:
        self._images[image_id] = image

    def register_model(self, model_id: ModelId, images: Iterable[Image]) -> None:
        self._models[model_id] = list(images)

    def observe(self, model_id, p='1/2'):
        "ATTN"
        model = self._models[model_id]
        truth = model[randrange(len(model))]
        data = random_image(base=truth, p=as_quantity(p)).value

        return (data, truth)

ImageModels = ImageSet()

#... add models and images here
