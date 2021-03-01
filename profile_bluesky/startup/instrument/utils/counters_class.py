from ..devices import scalerd
from ..session_logs import logger
logger.info(__file__)

__all__ = ['counters']


class CountersClass:
    """
    Holds monitor and detectors for scans. Our scans read these by default.

    Attributes
    ----------
    detectors : list of devices
        Detectors that will be read.
    extra_devices : list of devices
        Extra devices that will be read but explicitly not plottedd during
        scan. Keep in mind that it will "trigger and read", so if this takes a
        long time to trigger, it will slow down the scan.
    monitor : str
        Name of the scalerd channel that is used as monitor.
    """

    def __init__(self):
        super().__init__()
        # This will hold the devices instances.
        self._dets = [scalerd]
        self._mon = scalerd.monitor
        self._extra_devices = []

    def __repr__(self):

        read_names = [
            item.name for item in (self.detectors + self.extra_devices)
        ]

        plot_names = []
        for item in self.detectors:
            plot_names.extend(item.hints['fields'])

        return ("Counters settings\n"
                f"Monitor = {self._mon}\n"
                "Detectors:\n"
                f"  Read devices = {read_names}\n"
                f"  Plot components = {plot_names}")

    def __str__(self):
        return self.__repr__()

    def __call__(self, detectors, monitor=None):
        """
        Selects the plotting detector and monitor.

        For now both monitor and detector has to be in scalerd.

        Parameters
        ----------
        detectors : str or iterable
            Name(s) of the scalerd channels, or the detector instance to plot,
            if None it will not be changedd.
        monitor : str or int, optional
            Name or number of the scalerd channel to use as monitor, uses the
            same number convention as in SPEC. If None, it will not be changed.

        Example
        -------
        This selects the "Ion Ch 4" as detector, and "Ion Ch 1" as monitor:

        .. code-block:: python
            In[1]: counters('Ion Ch 4')

        Changes monitor to 'Ion Ch 3':

        .. code-block:: python
            In[2]: counters('Ion Ch 4', 'Ion Ch 3')

        Both 'Ion Ch 5' and 'Ion Ch 4' as detectors, and 'Ion Ch 3' as monitor:

        .. code-block:: python
            In[3]: counters(['Ion Ch 4', 'Ion Ch 5'], 'Ion Ch 3')

        Vortex as detector:

        .. code-block:: python
            In[4]: vortex = load_votex('xspress', 4)
            In[5]: counters(vortex)

        But you can mix scaler and other detectors:

        .. code-block:: python
            In[6]: counters([vortex, 'Ion Ch 5'])

        """

        self.detectors = detectors
        self.monitor = monitor

    @property
    def detectors(self):
        return self._dets

    @detectors.setter
    def detectors(self, value):
        if value is not None:
            # Ensures value is iterable.
            try:
                value = [value] if isinstance(value, str) else list(value)
            except TypeError:
                value = [value]

            # self._dets will hold the device instance.
            # scalerd is always a detector even if it's not plotted.
            self._dets = [scalerd]
            scalerd_list = []
            for item in value:
                if isinstance(item, str):
                    scalerd_list.append(item)
                else:
                    # item.select_plot_channels(True) This needs to be improved
                    self._dets.append(item)

            scalerd.select_plot_channels(scalerd_list)

    @property
    def monitor(self):
        return self._mon

    @monitor.setter
    def monitor(self, value):
        if value is not None:
            if isinstance(value, int):
                ch = getattr(scalerd.channels, 'ch{:02d}'.format(value+1))
                value = ch.s.name
            scalerd.monitor = value
            self._mon = scalerd.monitor

    @property
    def extra_devices(self):
        return self._extra_devices

    @extra_devices.setter
    def extra_devices(self, value):
        # Ensures value is iterable.
        try:
            value = list(value)
        except TypeError:
            value = [value]

        self._extra_devices = []
        for item in value:
            if isinstance(item, str):
                raise ValueError("Input has to be a device instance, not a "
                                 f"device name, but {item} was entered.")
            if item not in self.detectors:
                self._extra_devices.append(value)


counters = CountersClass()
