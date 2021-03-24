from .scaler import scalerd
from ..session_logs import logger
logger.info(__file__)

__all__ = ['counters']


class CountersClass:

    monitor = 'Ion Ch 4'
    detectors = [scalerd]

    def __call__(self, monitor=None, detectors=None):

        if monitor:
            if monitor not in scalerd.channels_name_map.keys():
                raise ValueError(f'{monitor} is not a scalerd channel.')
            else:
                scalerd.monitor = monitor
                self.monitor = monitor

        if detectors:
            if isinstance(detectors, str):
                detectors = [detectors]

            self.detectors = []
            _plot_channels = []
            for det in detectors:
                if isinstance(det, str):
                    self.detectors.append(scalerd)
                    _plot_channels.append(det)
                else:
                    self.detectors.append(det)

            scalerd.select_plot_channels(_plot_channels)


counters = CountersClass()
