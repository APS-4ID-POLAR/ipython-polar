from ..devices import scalerd
from ..session_logs import logger
logger.info(__file__)

__all__ = ['DEFAULTS', 'counters']


class defaults(object):

    def __init__(self):
        super().__init__()
        self._dets = []

    @property
    def detectors(self):
        if scalerd not in self._dets:
            self._dets.append(scalerd)
        return self._dets

    @detectors.setter
    def detectors(self, value):
        if not hasattr(value, '__iter__'):
            raise TypeError('value must be iterable.')

        if value not in self._dets:
            self._dets = list(value)


def counters(detectors, monitor='Time'):
    """
    Selects the plotting detector and monitor.

    For now both monitor and detector has to be in scalerd.

    Parameters
    ----------
    detectors : str or iterable
        Name(s) of the scalerd channels, or the detectors to plot
    monitor : str, optional
        Name of the scalerd channel to use as monitor, defaults to Time.
    """

    scalerd.select_monitor(monitor)

    if not hasattr(detectors, '__iter__'):
        detectors = [detectors]

    scalerd_list = []
    for item in detectors:
        if isinstance(item, str):
            scalerd_list.append(item)
        else:
            item.select_plot_channels(True)
            DEFAULTS.detectors += [item]

    scalerd.select_plot_channels(scalerd_list)


DEFAULTS = defaults()
