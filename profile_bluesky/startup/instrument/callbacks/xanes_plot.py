"""
Callback to plot normalized XANES on the fly
"""


__all__ = ['XanesCallback']



from ..session_logs import logger
logger.info(__file__)

from bluesky.callbacks.mpl_plotting import LivePlot
from bluesky.callbacks.core import make_class_safe, get_obj_fields
import warnings
from numpy import log

@make_class_safe
class XanesCallback(LivePlot):

    def __init__(self, y, monitor, x=None, *, transmission_mode=True,
                 legend_keys=None, xlim=None, ylim=None, ax=None, fig=None,
                 epoch='run', **kwargs):

        super().__init__(y, x=x, legend_keys=legend_keys, xlim=xlim, ylim=ylim,
                         ax=ax, fig=fig, epoch=epoch, **kwargs)

        def setup():
            # Run this code in start() so that it runs on the correct thread.
            nonlocal y, x, monitor, transmission_mode, legend_keys
            nonlocal xlim, ylim, ax, fig, epoch, kwargs
            import matplotlib.pyplot as plt
            with self.__setup_lock:
                if self.__setup_event.is_set():
                    return
                self.__setup_event.set()
            if fig is not None:
                if ax is not None:
                    raise ValueError("Values were given for both `fig` and `ax`. "
                                     "Only one can be used; prefer ax.")
                warnings.warn("The `fig` keyword arugment of LivePlot is "
                              "deprecated and will be removed in the future. "
                              "Instead, use the new keyword argument `ax` to "
                              "provide specific Axes to plot on.")
                ax = fig.gca()
            if ax is None:
                fig, ax = plt.subplots()
            self.ax = ax

            if legend_keys is None:
                legend_keys = []
            self.legend_keys = ['scan_id'] + legend_keys
            if x is not None:
                self.x, *others = get_obj_fields([x])
            else:
                self.x = 'seq_num'
            self.y, *others = get_obj_fields([y])
            self.monitor, *others = get_obj_fields([monitor])
            self.transmission_mode=transmission_mode
            self.ax.set_ylabel(y)
            self.ax.set_xlabel(x or 'sequence #')
            if xlim is not None:
                self.ax.set_xlim(*xlim)
            if ylim is not None:
                self.ax.set_ylim(*ylim)
            self.ax.margins(.1)
            self.kwargs = kwargs
            self.lines = []
            self.legend = None
            self.legend_title = " :: ".join([name for name in self.legend_keys])
            self._epoch_offset = None  # used if x == 'time'
            self._epoch = epoch

        self.__setup = setup

    def start(self,doc):
        super().start(doc)
        self.ax.set_ylabel('XANES')

    def event(self, doc):
        "Unpack data from the event and call self.update()."
        # This outer try/except block is needed because multiple event
        # streams will be emitted by the RunEngine and not all event
        # streams will have the keys we want.
        try:
            # This inner try/except block handles seq_num and time, which could
            # be keys in the data or accessing the standard entries in every
            # event.
            try:
                new_x = doc['data'][self.x]
            except KeyError:
                if self.x in ('time', 'seq_num'):
                    new_x = doc[self.x]
                else:
                    raise
            new_y = doc['data'][self.y]
            new_monitor = doc['data'][self.monitor]

            if transmission_mode:
                new_xanes = log(new_monitor/new_y)
            else:
                new_xanes = new_y/new_monitor

        except KeyError:
            # wrong event stream, skip it
            return

        # Special-case 'time' to plot against against experiment epoch, not
        # UNIX epoch.
        if self.x == 'time' and self._epoch == 'run':
            new_x -= self._epoch_offset

        self.update_caches(new_x, new_xanes)
        self.update_plot()
        super().event(doc)
