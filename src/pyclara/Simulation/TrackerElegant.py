import pyclara
import sdds
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from scipy import constants
import os


class Elegant_runner():
    def __init__(self, elegant_lte, elegant_ele, sdds_input):
        with open(elegant_lte, 'r') as r:
            self.elegant_lte = r.read()
        with open(elegant_ele, 'r') as r:
            self.elegant_ele = r.read()
        self.sdds_input = sdds.load(sdds_input)


    def write_elegant_input(self,run_dir,name):
        self.run_dir = run_dir
        self.name = name
        os.makedirs(self.run_dir, exist_ok=True)
        filepath1 = os.path.join(self.run_dir, f'{self.name}.lte')
        filepath2 = os.path.join(self.run_dir, f'{self.name}.ele')
        filepath3 = os.path.join(self.run_dir, f'{self.name}.sdds')
        with open(filepath1, 'w') as f:
            f.write(self.elegant_lte)
        with open(filepath2, 'w') as f:
            f.write(self.elegant_ele)
        self.sdds_input.mode = sdds.SDDS.SDDS_BINARY
        self.sdds_input.save(filepath3)

    def run (self):
        cmd = [
            "/lib64/mpich/bin/mpirun",
            "-np", "6",
            "/elegant/elegant/bin/Linux-x86_64/Pelegant",
            f"{self.name}.ele"
        ]
        result = subprocess.run(
            cmd,
            cwd=self.run_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print(result.stdout)

    def read_elegant_output(self):
        pass

    def elegant_ele_update_with_dict(self, inputdic, template):
        f = pyclara.Converters.elegant_ele()
        f.read(template)
        for k,v in inputdic.items():
            if k == "lattice":
                f.run_setup["lattice"] = v
        f.run_setup["use_beamline"] = f'{self.linename}_2'

        f.run_setup['p_central'] = inputdic['p_central']
        f.run_setup['s_start'] = s + inputdic['s_start']
        f.twiss_output['beta_x'] = para['beta_x']
        f.twiss_output['beta_y'] = para['beta_y']
        f.twiss_output['alpha_x'] = para['alpha_x']
        f.twiss_output['alpha_y'] = para['alpha_y']
        f.twiss_output['eta_x'] = para['eta_x']
        f.twiss_output['eta_y'] = para['eta_y']
        f.twiss_output['etap_x'] = para['etap_x']
        f.twiss_output['etap_y'] = para['etap_y']






