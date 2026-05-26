import matplotlib.pyplot as _plt
import numpy as _np

def All(xsuite_twiss) :

    _plt.subplot(5,1,1)
    Beta(xsuite_twiss, vertical_stack=True)

    _plt.subplot(5,1,2)
    Alpha(xsuite_twiss, vertical_stack=True)

    _plt.subplot(5,1,3)
    Psi(xsuite_twiss, vertical_stack=True)

    _plt.subplot(5,1,4)
    Eta(xsuite_twiss, vertical_stack=False)


def Beta(xsuite_twiss, linestyle = "-", marker=None, sOffset = 0, vertical_stack = False) :
    s = _np.array(xsuite_twiss['s'])
    betax = _np.array(xsuite_twiss['betx'])
    betay = _np.array(xsuite_twiss['bety'])

    # remove any offset in s
    s = s + sOffset

    _plt.plot(s,betax, label=r'XSuite $\beta_x$', linestyle = linestyle, marker = marker)
    _plt.plot(s,betay, label=r'XSuite $\beta_y$', linestyle = linestyle, marker = marker)

    if vertical_stack :
        _plt.xlabel('')
        _plt.gca().xaxis.set_visible(False)
    else :
        _plt.xlabel("s [m]")

    _plt.ylabel(r'$\beta_{x,y}$ [m]')
    _plt.legend()

def Alpha(xsuite_twiss, linestyle="-", marker=None, s0offset=0, vertical_stack=False):
    s = _np.array(xsuite_twiss['s'])
    alphax = _np.array(xsuite_twiss['alfx'])
    alphay = _np.array(xsuite_twiss['alfy'])

    # remove any offset in s
    s = s + sOffset

    _plt.plot(s, alphax, label=r'XSuite $\alpha_x$', linestyle=linestyle, marker=marker)
    _plt.plot(s, alphay, label=r'XSuite $\alpha_y$', linestyle=linestyle, marker=marker)

    if vertical_stack:
        _plt.xlabel('')
        _plt.gca().xaxis.set_visible(False)
    else:
        _plt.xlabel("s [m]")

    _plt.ylabel(r'$\alpha_{x,y}$ [m]')
    _plt.legend()

def Psi(xsuite_twiss, linestyle="-", marker=None, s0offset=0, vertical_stack=False):
    s = _np.array(xsuite_twiss['s'])
    psix = _np.array(xsuite_twiss['mux'])/_np.pi
    psiy = _np.array(xsuite_twiss['muy'])/_np.pi

    # remove any offset in s
    s = s + sOffset

    _plt.plot(s, psix, label=r'XSuite $\psi_x$', linestyle=linestyle, marker=marker)
    _plt.plot(s, psiy, label=r'XSuite $\psi_y$', linestyle=linestyle, marker=marker)

    if vertical_stack:
        _plt.xlabel('')
        _plt.gca().xaxis.set_visible(False)
    else:
        _plt.xlabel("s [m]")

    _plt.ylabel(r'$\psi_{x,y}$ [$\pi$] ')
    _plt.legend()

def Eta(xsuite_twiss, linestyle = "-", marker=None, s0offset = 0, vertical_stack = False) :
    s = _np.array(xsuite_twiss['s'])
    etax = _np.array(xsuite_twiss['dx'])
    etay = _np.array(xsuite_twiss['dy'])

    # remove any offset in s
    s = s + sOffset

    _plt.plot(s,etax, label=r'XSuite $\eta_x$', linestyle = linestyle, marker = marker)
    _plt.plot(s,etay, label=r'XSuite $\eta_y$', linestyle = linestyle, marker = marker)

    if vertical_stack :
        _plt.xlabel('')
        _plt.gca().xaxis.set_visible(False)
    else :
        _plt.xlabel("s [m]")

    _plt.ylabel(r'$\eta_{x,y}$ [m]')
    _plt.legend()

