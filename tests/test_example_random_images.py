from __future__ import annotations

from itertools import chain

from frplib.examples.random_images import (ImageModels, clockwise, counter_clockwise,
                                           reflect_image_vertically, invert_image,
                                           conway, black_pixels, pixel0, pixel1,
                                           as_image, get_component)

from frplib.kinds      import Kind, kind, weighted_as
from frplib.utils      import irange
from frplib.vec_tuples import vec_tuple

def test_image_invariants():
    "tests simple invariants of image operations on example images"
    aich = ImageModels.image('H')
    eff = ImageModels.image('F')
    pulsar = ImageModels.image('pulsar')

    assert eff == clockwise(counter_clockwise(eff))
    assert eff == clockwise(clockwise(clockwise(clockwise(eff))))
    assert eff == reflect_image_vertically(reflect_image_vertically(eff))

    assert pulsar == conway(conway(conway(pulsar)))

    assert aich == invert_image(invert_image(aich))

    u = as_image(pixel0 * 4 + pixel1 * 8 + pixel0 * 4, 4, 4)
    assert black_pixels(u) == vec_tuple(8)

    v = as_image(pixel1 * 4 + pixel0 * 8 + pixel1 * 4, 4, 4)

    assert v ^ get_component(1) == as_image(pixel1 * 4 + pixel0 * 12, 4, 4)
    assert v ^ get_component(2) == as_image(pixel0 * 12 + pixel1 * 4, 4, 4)
