import numpy as _np

def yaml2acccoords(yaml_dict = None,
                    start_element = "CLA-FEA-MAG-QUAD-13",
                    end_element = "CLA-FED-SIM-DUMP-01-START") :

    yaml_elements = yaml_dict['elements']

    s_delta  = []
    s_start  = []
    s_centre = []
    s_end    = []
    x = []
    y = []
    l = []
    angle = []
    tilt = []

    first = True
    converting = False


    for k in yaml_elements.keys():

        if k == start_element:
            converting = True

        if not converting:
            continue

        if k == end_element:
            converting = False

        e = yaml_elements[k]
        length = e['length']

        if first :
            first = False
            centre_old = _np.array(e['centre'])

        type   = e['type']
        centre = _np.array(e['centre'])
        length = _np.array(e['length'])
        angle = 0

        start = _np.array([0,0,0])
        centre_delta = _np.array([0,0,0])
        end = _np.array([0,0,0])

        if type != 'dipole' :
            centre_delta = centre - centre_old
            start = centre - centre_delta/2
            end = centre + centre_delta/2
            s_delta.append(_np.linalg.norm(centre_delta))
        else :
            # print("dipole")
            angle = e['angle']
            centre_delta = centre - centre_old
            s_delta.append(_np.linalg.norm(centre_delta))


        if len(s_centre) == 0 :
            s_start.append(-length/2)
            s_centre.append(0)
            s_end.append(length/2)
        else :
            s_start.append(s_centre[-1]+s_delta[-1]-length/2)
            s_end.append(s_centre[-1]+s_delta[-1]+length/2)
            s_centre.append(s_centre[-1]+s_delta[-1])

        # print(k, type, length, angle, s_centre[-1])

        # update centre old for next iteration
        centre_old = centre

    s_delta  = _np.array(s_delta)
    s_start  = _np.array(s_start)
    s_centre = _np.array(s_centre)
    s_end    = _np.array(s_end)

    s0 = s_start[0]
    s_start -= s0
    s_centre -= s0
    s_end -= s0

    return s_start, s_centre, s_end


