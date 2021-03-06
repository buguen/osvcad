# coding: utf-8

r"""Flat plate with holes Python creation script"""

from ccad.model import prism, filling, ngon, cylinder, translated, box

units = 'mm'

e = 10
l = 200
w = 100

hole_d = 10

hole_positions = ((50, -25), (50, 25), (-50, -25), (-50, 25))

plate = translated(box(l, w, e), (-l /2, -w/2, 0))

cylinders = list()

for (x, y) in hole_positions:
    cylinders.append(translated(cylinder(hole_d / 2., e), (x, y, 0)))

for c in cylinders:
    plate -= c
part = plate

anchors = dict()
for i, (x, y) in enumerate(hole_positions):
    anchors[i] = {"position": (x, y, e),
                  "direction": (0., 0., 1.),
                  "dimension": hole_d,
                  "description": "%s mm hole" % hole_d}

if __name__ == '__main__':
    # part.to_step("plate_with_holes.step", precision_mode=0, assembly=0,
    #              schema='AP203', surface_curve_mode=1, transfer_mode=0,
    #              units=units)
    import ccad.display as cd
    v = cd.view()
    v.display(part, color=(0.1, 0.1, 1.0), transparency=0.3)
    for k, anchor in anchors.items():
        v.display_vector(origin=anchor['position'],
                         direction=anchor['direction'])
    cd.start()
