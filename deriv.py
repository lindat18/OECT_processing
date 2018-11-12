from scipy import signal as sps
import numpy as np
import warnings

"""
Derivative for generating gm from Id-Vg plots
"""


def gm_deriv(v, i, method='raw', fit_params={'window': 11, 'polyorder': 2, 'deg': 8}):
    if method is 'sg':
        # Savitsky-Golay method
        if not fit_params['window'] & 1:  # is odd
            fit_params['window'] += 1
        gml = sps.savgol_filter(i.T, window_length=fit_params['window'],
                                polyorder=fit_params['polyorder'], deriv=1,
                                delta=v[2] - v[1])[0, :]
    elif method is 'raw':
        # raw derivative
        gml = np.gradient(i.flatten(), v[2] - v[1])

    elif method is 'poly':
        # polynomial fit
        funclo = np.polyfit(v, i, fit_params['deg'])
        gml = np.gradient(np.polyval(funclo, v), (v[2] - v[1]))

    else:
        warnings.warn('Bad gm_method, aborting')
        return

    return gml
