"""
query_optics.py
---------------
Query Twiss parameters and emittances at a named element from Elegant SDDS output.

Usage:
    python query_optics.py <ElementName> [--results-dir PATH]

Example:
    python query_optics.py CLA-FEA-SIM-DIP-04-END
    python query_optics.py CLA-FEA-DIA-BPM-09 --results-dir /path/to/results
"""

import struct
import re
import argparse
from pathlib import Path


# ---------------------------------------------------------------------------
# Low-level SDDS binary helpers
# ---------------------------------------------------------------------------

def _parse_header(data):
    """Return (params, cols, data_offset) from a binary SDDS file."""
    text = data.decode("latin-1", errors="replace")
    lines = text.split("\n")
    params, cols = [], []
    header_end_line = 0
    for i, line in enumerate(lines):
        if line.startswith("&data"):
            header_end_line = i
            break
        if line.startswith("&parameter"):
            name  = re.search(r"name=(\S+?),", line)
            ptype = re.search(r"type=(\w+)", line)
            fixed = re.search(r"fixed_value=(\S+)", line)
            params.append({
                "name":        name.group(1)  if name  else "",
                "type":        ptype.group(1) if ptype else "",
                "fixed_value": fixed.group(1).rstrip(", &end") if fixed else None,
            })
        elif line.startswith("&column"):
            name  = re.search(r"name=(\S+?),", line)
            ctype = re.search(r"type=(\w+)", line)
            units = re.search(r"units=([^\s,]+)", line)
            cols.append({
                "name":  name.group(1)  if name  else "",
                "type":  ctype.group(1) if ctype else "",
                "units": units.group(1) if units else "",
            })
    data_offset = sum(len(l.encode("latin-1")) + 1 for l in lines[: header_end_line + 1])
    return params, cols, data_offset


def _read_val(data, offset, dtype):
    """Read a single value of the given SDDS type; return (value, new_offset)."""
    if dtype == "double":
        return struct.unpack_from("<d", data, offset)[0], offset + 8
    elif dtype in ("long", "ulong"):
        return struct.unpack_from("<i", data, offset)[0], offset + 4
    elif dtype == "string":
        length = struct.unpack_from("<i", data, offset)[0]
        offset += 4
        return data[offset: offset + length].decode("latin-1"), offset + length
    return None, offset


def _find_element_offset(data, element_name):
    """
    Locate the byte offset of the ElementName string in the binary payload.
    SDDS stores strings as int32 length + bytes, so we search for that pattern.
    """
    needle = len(element_name).to_bytes(4, "little") + element_name.encode("latin-1")
    positions = []
    start = 0
    while True:
        pos = data.find(needle, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


# ---------------------------------------------------------------------------
# Public readers
# ---------------------------------------------------------------------------

def read_twiss(twi_path, element_name):
    """
    Return a dict of Twiss parameters at *element_name* from a .twi file.
    Keys: s, alphax, betax, gammax, etax, etaxp, alphay, betay, gammay, etay
    """
    with open(twi_path, "rb") as f:
        data = f.read()

    positions = _find_element_offset(data, element_name)
    if not positions:
        return None

    # Column layout before ElementName (14 doubles × 8 bytes = 112 bytes):
    # s, betax, alphax, psix, etax, etaxp, xAperture,
    # betay, alphay, psiy, etay, etayp, yAperture, pCentral0
    leading_doubles = [
        "s", "betax", "alphax", "psix", "etax", "etaxp", "xAperture",
        "betay", "alphay", "psiy", "etay", "etayp", "yAperture", "pCentral0",
    ]
    row_start = positions[0] - len(leading_doubles) * 8
    offset = row_start
    vals = {}
    for name in leading_doubles:
        vals[name], offset = _read_val(data, offset, "double")

    # Derived Twiss gamma
    vals["gammax"] = (1 + vals["alphax"] ** 2) / vals["betax"]
    vals["gammay"] = (1 + vals["alphay"] ** 2) / vals["betay"]
    return vals


def read_sigma(sig_path, element_name):
    """
    Return a dict of beam parameters at *element_name* from a .sig file.
    Keys: Sx, Sy, Ss, Sdelta, ex, enx, ey, eny,
          betaxBeam, alphaxBeam, betayBeam, alphayBeam
    """
    with open(sig_path, "rb") as f:
        data = f.read()

    positions = _find_element_offset(data, element_name)
    if not positions:
        return None

    pos = positions[0]

    # Skip past ElementName to read ElementOccurence and ElementType
    offset = pos + 4 + len(element_name)          # past ElementName
    _occ, offset  = _read_val(data, offset, "long")
    _etype, offset = _read_val(data, offset, "string")

    # Sigma-matrix columns that follow (all doubles):
    sigma_cols = [
        "s1","s12","s13","s14","s15","s16","s17",
        "s2","s23","s24","s25","s26","s27",
        "s3","s34","s35","s36","s37",
        "s4","s45","s46","s47",
        "s5","s56","s57",
        "s6","s67",
        "s7",
        "ma1","ma2","ma3","ma4","ma5","ma6","ma7",
        "minimum1","minimum2","minimum3","minimum4","minimum5","minimum6","minimum7",
        "maximum1","maximum2","maximum3","maximum4","maximum5","maximum6","maximum7",
        "Sx","Sxp","Sy","Syp","Ss","Sdelta","St",
        "ex","enx","ecx","ecnx",
        "ey","eny","ecy","ecny",
        "betaxBeam","alphaxBeam","betayBeam","alphayBeam",
    ]
    vals = {}
    for name in sigma_cols:
        vals[name], offset = _read_val(data, offset, "double")

    return vals


# ---------------------------------------------------------------------------
# Pretty-print
# ---------------------------------------------------------------------------

def format_results(element_name, twiss, sigma):
    sep = "─" * 55
    lines = []
    lines.append(f"\n{sep}")
    lines.append(f"  Element : {element_name}")
    if twiss:
        lines.append(f"  s       : {twiss['s']:.4f} m")
    lines.append(sep)

    if twiss:
        lines.append("\n  Twiss parameters (design optics)")
        lines.append(f"  {'':20s}  {'Horizontal':>14}  {'Vertical':>14}")
        lines.append(f"  {'alpha':20s}  {twiss['alphax']:>14.6f}  {twiss['alphay']:>14.6f}")
        lines.append(f"  {'beta  [m]':20s}  {twiss['betax']:>14.6f}  {twiss['betay']:>14.6f}")
        lines.append(f"  {'gamma [1/m]':20s}  {twiss['gammax']:>14.6f}  {twiss['gammay']:>14.6f}")
        lines.append(f"  {'etax  [m]':20s}  {twiss['etax']:>14.6e}  {twiss['etay']:>14.6e}")
        lines.append(f"  {'etaxp':20s}  {twiss['etaxp']:>14.6e}")
    else:
        lines.append("  [Twiss file: element not found]")

    if sigma:
        bx = sigma["betaxBeam"]; ax = sigma["alphaxBeam"]
        by = sigma["betayBeam"]; ay = sigma["alphayBeam"]
        gx = (1 + ax**2) / bx if bx else float("nan")
        gy = (1 + ay**2) / by if by else float("nan")

        lines.append("\n  Twiss parameters (from beam sigma matrix)")
        lines.append(f"  {'':20s}  {'Horizontal':>14}  {'Vertical':>14}")
        lines.append(f"  {'alpha':20s}  {ax:>14.6f}  {ay:>14.6f}")
        lines.append(f"  {'beta  [m]':20s}  {bx:>14.6f}  {by:>14.6f}")
        lines.append(f"  {'gamma [1/m]':20s}  {gx:>14.6f}  {gy:>14.6f}")

        lines.append("\n  Emittances")
        lines.append(f"  {'':20s}  {'Horizontal':>14}  {'Vertical':>14}")
        lines.append(f"  {'geom  [m]':20s}  {sigma['ex']:>14.6e}  {sigma['ey']:>14.6e}")
        lines.append(f"  {'norm  [m]':20s}  {sigma['enx']:>14.6e}  {sigma['eny']:>14.6e}")

        lines.append("\n  Beam sizes")
        lines.append(f"  Sx (rms x)        = {sigma['Sx']*1e6:.4f} um")
        lines.append(f"  Sy (rms y)        = {sigma['Sy']*1e6:.4f} um")
        lines.append(f"  Ss (bunch length) = {sigma['Ss']*1e3:.4f} mm")
        lines.append(f"  Sdelta (rms dp/p) = {sigma['Sdelta']:.4e}")
    else:
        lines.append("  [Sigma file: element not found]")

    lines.append(f"{sep}\n")
    return "\n".join(lines)


def print_results(element_name, twiss, sigma):
    print(format_results(element_name, twiss, sigma))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Query Twiss + emittance from Elegant SDDS output.")
    parser.add_argument("element", help="Element name, e.g. CLA-FEA-SIM-DIP-04-END")
    parser.add_argument(
        "--results-dir",
        default="/mnt/iusers01/fatpou01/phy01/g44148sw/scratch/FEBE_results",
        help="Directory containing FEBE.twi and FEBE.sig",
    )
    args = parser.parse_args()

    results = Path(args.results_dir)
    twi_path = results / "FEBE.twi"
    sig_path = results / "FEBE.sig"

    twiss = read_twiss(twi_path, args.element) if twi_path.exists() else None
    sigma = read_sigma(sig_path, args.element) if sig_path.exists() else None

    if twiss is None and sigma is None:
        print(f"Element '{args.element}' not found in either FEBE.twi or FEBE.sig.")
        print(f"Results directory: {results}")
        return

    output = format_results(args.element, twiss, sigma)
    print(output)

    # Save to twiss_result subfolder
    out_dir = results / "twiss_result"
    out_dir.mkdir(exist_ok=True)
    safe_name = args.element.replace("/", "_").replace(" ", "_")
    out_path = out_dir / f"{safe_name}_optics.txt"
    with open(out_path, "w") as f:
        f.write(output)
    print(f"  Saved to: {out_path}")


if __name__ == "__main__":
    main()
