# 227, the Back Dimension: the disc's script gave the second BlueMeramon its line and no battle, so it repeated the line
# for ever; it now fights as the other three in this room do.
from dw import *
from dw.text import text
from dw.base.back_dimension_227 import dimension, bluemeramon3

blue = take_over(bluemeramon3)

@blue.on_talk
def talk():
    recruitable(blue, line=text.s186.sec8.u0)
