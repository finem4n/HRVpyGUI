import datetime
import platform
import os

import neurokit2 as nk
import numpy as np
import scipy
import pandas as pd


def timestampsToTime(timestamps, timestamp0):
    time = []
    for i in range(len(timestamps)):
        time.append((datetime.datetime.fromisoformat(timestamps[i]) - datetime.datetime.fromisoformat(timestamp0)).total_seconds())

    return time


def getRR(ecg_cleaned, timestamps, fs: float):
    """Form an RRI DataFrame from ECG Signal"""

    _, peaks_info = nk.ecg_peaks(ecg_cleaned=ecg_cleaned, sampling_rate=fs)

    peaks_timestamps = [timestamps[x] for x in peaks_info["ECG_R_Peaks"]]
    rri = np.diff(peaks_timestamps)

    peaks_timestamps.pop(0)

    rr_timestamps = np.array(peaks_timestamps) / 1000

    dataframe = pd.DataFrame(rri, columns=["RR Intervals [ms]"])
    dataframe["Time [s]"] = rr_timestamps

    return dataframe, peaks_info


# Modified function from neurokit2
# 1. Fix issue when last 2 points aren't detrended
# In Tarvainen et al., 2002 signal's length is defined as N-1, because of extraction from ECG.
# In neurokit2 we are taking RRi signal, so the length must be equal to N.
# Because of this I -> R^N and D_N -> R^(N-2)(N)
# 2. Modification elevates output to mean
def signal_detrend_tarvainen2002(signal, regularization=500):
    """Method by Tarvainen et al., 2002.
    - Tarvainen, M. P., Ranta-Aho, P. O., & Karjalainen, P. A. (2002). An advanced detrending method
    with application to HRV analysis. IEEE Transactions on Biomedical Engineering, 49(2), 172-175.
    """
    # Source:
    # https://github.com/neuropsychology/NeuroKit/blob/45c9ad90d863ebf4e9d043b975a10d9f8fdeb06b/neurokit2/signal/signal_detrend.py#L157

    N = len(signal)
    identity = np.eye(N)
    B = np.dot(np.ones((N, 1)), np.array([[1, -2, 1]]))  # pylint: disable=E1101
    D_2 = scipy.sparse.dia_matrix((B.T, [0, 1, 2]), shape=(N - 2, N))
    inv = np.linalg.inv(identity + regularization**2 * D_2.T @ D_2)
    z_stat = ((identity - inv)) @ signal

    trend = np.squeeze(np.asarray(signal - z_stat))

    return signal - trend + np.mean(signal)


def getUserPath():
    if platform.system() == 'Windows':
        path = os.path.expanduser('~user')

    elif platform.system() in ('Linux', 'Darwin'):
        path = os.path.expanduser('~')

    else:
        path = os.getcwd()

    return path
