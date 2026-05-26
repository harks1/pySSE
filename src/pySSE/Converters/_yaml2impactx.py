try :
    from impactx import elements as _elements
except ImportError:
    print("impactx not found, cannot convert yaml to impactx line")

from ._yaml2acccoords import yaml2acccoords

def loadyaml(filename):
    import yaml
    with open(filename, 'r') as f:
        yaml_dict = yaml.safe_load(f)

    return yaml_dict

def yaml2impactx(yaml_dict = None, start_element = "CLA-FEA-MAG-QUAD-13", end_element = "CLA-FED-SIM-DUMP-01-START"):

    yaml_elements = yaml_dict['elements']

    s_start, s_centre, s_end = yaml2acccoords(yaml_dict, start_element, end_element)

    ix_converted = []
    ix_idx = []

    converting = False

    i = 0
    for k in yaml_elements.keys():

        e = yaml_elements[k]
        t = e['type']
        l = e['length']

        if k == start_element:
            converting = True

        if not converting:
            continue

        if k == end_element:
            converting = False

        ix_e = None

        if t == 'quadrupole':
            ix_e = _elements.Quad(name=k, ds=l, k=e['k1l']/l) # TODO not sure about this division as the ks look large
            ix_idx.append(i)
        else :
            pass

        if ix_e is not None :
            ix_converted.append(ix_e)

        i += 1

    # line
    ix_line = []

    # make drifts
    for i in range(0,len(ix_converted)) :
        name = "drift_"+str(i)
        ix_line.append(ix_converted[i])
        try :
            ix_line.append(_elements.Drift(name=name, ds=s_start[ix_idx[i+1]]-s_end[ix_idx[i]]))
        except IndexError :
            pass

    return ix_line, ix_idx




