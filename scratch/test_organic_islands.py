#!/usr/bin/env python3
import sys, os, re, math
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, CH_LIMBS, CH_GAP, CH_SPIRAL, poly_path, pt, n, smooth_island, circle_d, _chaikin, smooth_closed

# Let's see how Tube.piece behaves with different rounds and segmentation
body = Tube(CH_BODY_KNOTS)
sx = body.s_at_x

print("Tube total L:", body.L)
print("s at x=886:", sx(886))
print("s at x=806:", sx(806))
print("s at x=754:", sx(754))
print("s at x=682:", sx(682))
print("s at x=546:", sx(546))
print("s at x=470:", sx(470))
