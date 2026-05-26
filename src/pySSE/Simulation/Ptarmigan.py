import os as _os
import shutil as _shutil

class RunnerPtarmigan :

    def __init__(self, ptarmiganExePath):
        # control
        self.control = {}
        self.control['radiation_reaction'] = True
        self.control['pair_creation'] = True
        self.control['pol_resolved'] = False
        self.control['classical'] = False
        self.control['lcfa'] = False
        self.control['bandwidth_correction'] = False
        self.control['dt_multiplier'] = 1.0
        self.control['increase_pair_rate_by'] = 1.0
        self.control['rng_seed'] = 0
        self.control['track_secondaries'] = True
        self.control['select_multiplicity'] = None
        self.control['stop_at_time'] = None

        self.laser = {}
        self.laser['a0'] = None
        self.laser['wavelength'] = None
        self.laser['omega'] = None
        self.laser['polarization'] = None
        self.laser['waist'] = None
        self.laser['envelope'] = None
        self.laser['fwhm_duration'] = None
        self.laser['n_cycles'] = None
        self.laser['chirp_coeff'] = None

        self.beam = {}
        self.beam['n'] = None
        self.beam['species'] = None
        self.beam['nreal'] = None
        self.beam['charge'] = None
        self.beam['gamma'] = None
        self.beam['sigma'] = None
        self.beam['rms_divergence'] = None
        self.beam['spectrum'] = {"function": None,
                                 "min": None,
                                 "max": None}
        self.beam['radius'] = None
        self.beam['length'] = None
        self.beam['energy_chirp'] = None
        self.beam['stokes_pars'] = [0, 0, 0]
        self.beam['collision_angle'] = 0
        self.beam['offset'] = [0, 0, 0]
        self.beam['from_hdf5'] = {"file": None,
                                  "distance_between_ips": None,
                                  "auto_timing": True,
                                  "min_energy": 0,
                                  "max_angle": "pi"}


        self.output = {}
        self.output['ident'] = "no prefix"
        self.output['min_energy'] = 0
        self.output['max_angle'] = "pi"
        self.output['coordinate_system'] = "laser"
        self.output['discard_background'] = False
        self.output['units'] = "auto"
        self.output['dump_all_particles'] = None
        self.output['dump_decayed_photons'] = False
        self.output['file_format'] = None
        self.output['electron'] = None
        self.output['photon'] = None
        self.output['positron'] = None
        self.output['intermediate'] = None

        self.stats = {}
        self.stats['file_format'] = None
        self.stats['electron'] = None
        self.stats['photon'] = None
        self.stats['positron'] = None
        self.stats['intermediate'] = None

        self.fileIncrement = 0

    def run(self, runDir = "./ptarmigan_run", saveRun = False):

        # create run dir (increment if it exists)
        try :
            _os.mkdir(runDir)
        except FileExistsError :
            self.fileIncrement += 1
            runDir = f"{runDir}_{self.fileIncrement}"
            self.run(runDir = runDir, saveRun = saveRun)

        # create input file
        self.writeInputFile(f"{runDir}/ptarmigan_input.txt")

        # run

        if not saveRun :
            self._cleanUp(runDir)

        # load output


        pass

    def writeInputFile(self, file_name = "ptarmigan_input"):
        f = open(file_name, 'w')
        self._writeDict(f,"control", self.control)
        self._writeDict(f,"laser", self.laser)
        self._writeDict(f,"beam", self.beam)
        self._writeDict(f,"output", self.output)
        self._writeDict(f,"stats", self.stats)
        f.close()

    def _writeDict(self, f, dict_name, dict_to_write, ident = 2):

        identstr = " "*ident

        # check if all values are None
        skip = True
        for k in dict_to_write:
            v = dict_to_write[k]
            if v is not None:
                skip = False

        if skip :
            return

        f.write(f"{dict_name}:\n")
        for k in dict_to_write.keys():
            v = dict_to_write[k]
            if v is not None:
                if isinstance(v, dict) :
                    if v[list(v)[0]] is not None :
                        self._writeDict(f, k, v, ident+2)
                else :
                    if isinstance(v, bool) :
                        if v :
                            v = "true"
                        else :
                            v = "false"
                    f.write(f"{identstr}{k}: {v}\n")

    def _cleanUp(self, runDir):
        _shutil.rmtree(runDir)
