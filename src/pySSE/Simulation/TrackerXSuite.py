from .TrackerBase import TrackerBase as _TrackerBase

class TrackerXSuite(_TrackerBase):

    def __init__(self, xsuite_env):
        ''' xsuite_env with ony one line'''
        self.xsuite_env = xsuite_env

    def track(self, particles):
        return particles

    @staticmethod
    def makeFromElegant(self,
                        elegant_lte,
                        start_element = None,
                        end_element = None,
                        elegant_twi = None):
        pass

    @staticmethod
    def makeParticlesFromTwiss(self):
        pass
