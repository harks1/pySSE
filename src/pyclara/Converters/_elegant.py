import re as _re
from collections import defaultdict as _defaultdict
import sdds 
import numpy as np
import h5py
from scipy import constants

def elegant_lte_loader(filename):
    with open(filename) as f:
        content = f.read()

    # Remove comments (! and %)
    content = _re.sub(r'[!%].*', '', content)

    # Join continuation lines
    content = _re.sub(r'&\s*\n', ' ', content)

    # Find all name&type blocks: NAME: TYPE, key=val, key=val ...
    pattern = _re.compile(
        r'([\w-]+)\s*:\s*(\w+)\s*,?\s*([^;]*)',
        _re.IGNORECASE
    )

    elements = _defaultdict(list)

    for match in pattern.finditer(content):
        name, etype, params_str = match.groups()
        params = {"NAME": name.upper()}

        for kv in _re.findall(r'(\w+)\s*=\s*([^,\n]+)', params_str):
            key, val = kv
            val = val.strip().strip('"')
            try:
                params[key.upper()] = float(val)
            except ValueError:
                params[key.upper()] = val

        if etype.upper() == "LINE" :
            val = _re.findall(r'=\((.+)\)',params_str)
            elist = []
            for eval  in val[0].split(","):
                elist.append(eval.strip())
            params["LINE"] = elist

        params['TYPE'] = etype.upper()
        elements[name] = params

    return dict(elements)

def fbpic2sdds(inputfile, outputfile, particles_group):

    x_all = []
    y_all= []
    z_all = []
    px_all = []
    py_all = []
    pz_all = []
    c_all = 0.0
    with h5py.File(inputfile, 'r') as f:

        iteration = list(f["data"].keys())[0]

        for particle in particles_group :
                x_all.append(f[f"/data/{iteration}/particles/{particle}/position/x"][:])
                y_all.append(f[f"/data/{iteration}/particles/{particle}/position/y"][:])
                z_all.append(f[f"/data/{iteration}/particles/{particle}/position/z"][:])
                px_all.append(f[f"/data/{iteration}/particles/{particle}/momentum/x"][:])
                py_all.append(f[f"/data/{iteration}/particles/{particle}/momentum/y"][:])
                pz_all.append(f[f"/data/{iteration}/particles/{particle}/momentum/z"][:])
                c_all += f[f"/data/{iteration}/particles/{particle}/charge"].attrs["value"]
    x  = np.concatenate(x_all)
    y  = np.concatenate(y_all)
    z  = np.concatenate(z_all)
    px = np.concatenate(px_all)
    py = np.concatenate(py_all)
    pz = np.concatenate(pz_all)
    n  = np.arange(1, len(x)+1)

    t = z / constants.c
    dt = t - np.mean(t)
    p = np.sqrt(px**2+py**2+pz**2)
    xp = px/p
    yp = py/p


    sdds_obj = sdds.SDDS()
    
    sdds_obj.setDescription(
        "SDDS files converted from hdf5 files from FBPIC",
        "x xp y yp t p dt" 
    )
    sdds_obj.defineParameter("c", units='C', description='Charge of the beam')
    sdds_obj.defineParameter("Particles", description='Number of particles',type=sdds.SDDS_LONG)
    sdds_obj.defineColumn("x",  units="m")
    sdds_obj.defineColumn("xp")
    sdds_obj.defineColumn("y",  units="m")
    sdds_obj.defineColumn("yp")
    sdds_obj.defineColumn("t",  units="s")
    sdds_obj.defineColumn("p",  units="m$be$nc")
    sdds_obj.defineColumn("dt", units="s")
    sdds_obj.defineColumn("particleID",type=sdds.SDDS_LONG)
    columns_page1 = {
        "x"  : x.tolist(),
        "xp" : xp.tolist(),
        "y"  : y.tolist(),
        "yp" : yp.tolist(),
        "t"  : t.tolist(),
        "p"  : p.tolist(),
        "dt" : dt.tolist(),
        "particleID" : n.tolist()
    }
    sdds_obj.setParameterValue("c", c_all , page=1)
    sdds_obj.setParameterValue("Particles", len(x) , page=1)
    for col_name, col_data in columns_page1.items():
        sdds_obj.setColumnValueList(col_name, col_data, page=1)

    sdds_obj.save(outputfile)

def sdds2fbpic(sddsfile) :
    f = sdds.load(sddsfile)
    xbeam = np.array(f.getColumnValueList("x"))
    ybeam = np.array(f.getColumnValueList("y"))
    xpbeam = np.array(f.getColumnValueList("xp"))
    ypbeam = np.array(f.getColumnValueList("yp"))
    dtbeam = np.array(f.getColumnValueList("dt"))
    pbeam = np.array(f.getColumnValueList("p"))
    pxbeam = xpbeam * pbeam
    pybeam = ypbeam * pbeam

    return {"x" : xbeam, "y" : ybeam, "xp" : xpbeam, "yp" : ypbeam, "dt" : dtbeam, "p" : pbeam, "px" : pxbeam, "py" : pybeam}

def sdds2beam_dict(sddsfile) :
    f = sdds.load(sddsfile)
    x = np.array(f.getColumnValueList("x"))
    y = np.array(f.getColumnValueList("y"))
    xp = np.array(f.getColumnValueList("xp"))
    yp = np.array(f.getColumnValueList("yp"))
    t = np.array(f.getColumnValueList("t"))
    p = np.array(f.getColumnValueList("p"))

    x -= x.mean()
    y -= y.mean()
    xp -= xp.mean()
    yp -= yp.mean()
    t -= t.mean()
    p0 = p.mean()
    p -= p0

    zeta = t*constants.c
    delta = p/p0

    return {"x" : x,
            "xp" : xp,
            "y" : y,
            "yp" : yp,
            "zeta" : zeta,
            "delta" : delta}