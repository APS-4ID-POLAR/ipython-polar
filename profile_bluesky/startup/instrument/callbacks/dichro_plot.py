"""
Processed dichro data for plot.
"""

from ..session_logs import logger
logger.info(__file__)

__all__ = ['AutoDichroPlot']

from bluesky_widgets.models.auto_plot_builders import AutoPlotter
from bluesky_widgets.models.plot_builders import Lines
from bluesky_widgets.models.plot_specs import AxesSpec, FigureSpec
from numpy import log, array


def xanes(monitor, detector):
    absorption = log(array(monitor) / array(detector)).reshape(-1, 4)
    return absorption.mean(axis=1)


def xmcd(monitor, detector):
    absorption = log(array(monitor) / array(detector)).reshape(-1, 4)
    return (absorption[:, [0, 3]].mean(axis=1) -
            absorption[:, [1, 2]].mean(axis=1))


def downsampled(x):
    return array(x).reshape(-1, 4).mean(axis=1)


class AutoDichroPlot(AutoPlotter):
    def __init__(self, monitor="Ion Ch 4", detector="Ion Ch 5"):
        super().__init__()
        self._x_to_lines = {}  # map x variable to (xanes_lines, xmcd_lines)
        self._monitor = monitor
        self._detector = detector

    @property
    def monitor(self):
        return self._monitor

    @property
    def detector(self):
        return self._detector

    def handle_new_stream(self, run, stream_name):
        if stream_name != "primary":
            # Nothing to do for this stream.
            return

        # Look for the scan_type='dichro' hint
        scan_type = run.metadata["start"]["hints"].pop('scan_type', None)
        if scan_type != 'dichro':
            return

        # Detect x variable from hints in metadata.
        first_scan_dimension = run.metadata["start"]["hints"]["dimensions"][0]
        scanning_fields, _ = first_scan_dimension
        x = scanning_fields[0]
        # If we already have a figure for this x, reuse it (over-plot).
        try:
            (xanes_lines, xmcd_lines) = self._x_to_lines[x]
        except KeyError:
            # We don't have a figure for this x. Make one.
            xanes_axes = AxesSpec(x_label=x, title="XANES")
            xmcd_axes = AxesSpec(x_label=x, title="XMCD")
            figure = FigureSpec((xanes_axes, xmcd_axes),
                                title="XANES and XMCD")
            # Set up objects that will select the approriate data and do the
            # desired transformation for plotting.
            xanes_lines = Lines(
                x=lambda primary: downsampled(primary[x]),
                ys=[lambda primary: xanes(primary[self._monitor],
                                          primary[self._detector])],
                axes=xanes_axes,
            )
            xmcd_lines = Lines(
                x=lambda primary: downsampled(primary[x]),
                ys=[lambda primary: xmcd(primary[self._monitor],
                                         primary[self._detector])],
                axes=xmcd_axes,
            )
            self._x_to_lines[x] = (xanes_lines, xmcd_lines)
            # Keep track of these plot builders to enable *removing* runs from
            # them.
            self.plot_builders.append(xanes_lines)
            self.plot_builders.append(xmcd_lines)
            # Appending this figures list will trigger to view to show our new
            # figure.
            self.figures.append(figure)
        # Add this Run to the figure.
        xanes_lines.add_run(run)
        xmcd_lines.add_run(run)
