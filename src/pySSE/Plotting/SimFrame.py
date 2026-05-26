import matplotlib.pyplot as _plt
import numpy as _np

from ..Converters._yaml2acccoords import yaml2acccoords

def plotCoordinates(yaml_dict,
                    start_element = "CLA-FEA-MAG-QUAD-13",
                    end_element = "CLA-FED-SIM-DUMP-01-START"):

    s_start, s_centre, s_end = yaml2acccoords(yaml_dict, start_element, end_element)

    yaml_elements = yaml_dict['elements']

    x = []
    y = []
    z = []

    for e in yaml_elements.keys()  :
        c = _np.array(yaml_elements[e]['centre'])

        x.append(c[0])
        y.append(c[1])
        z.append(c[2])

    x = _np.array(x)
    y = _np.array(y)
    z = _np.array(z)

    aspect = (x.max() - z.min()) / (z.max() - z.min()) * 3

    if len(_plt.get_fignums()) == 0 :
        _plt.figure(figsize=(7, 7*aspect))

    _plt.plot(z, x, '+', label=e)
    _plt.tight_layout()

