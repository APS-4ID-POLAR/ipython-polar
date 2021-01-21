""" Generate plots """

from ..session_logs import logger
logger.info(__file__)

__all__ = ['start_dichro_plot']

from bluesky_widgets.qt.figures import QtFigures
from bluesky_widgets.utils.streaming import stream_documents_into_runs
from ..framework import RE
from ..callbacks import AutoDichroPlot


# TODO: Is there a better way to do this?
def start_dichro_plot():
    dichro_model = AutoDichroPlot()
    dichro_view = QtFigures(dichro_model.figures)
    dichro_view.show()
    RE.subscribe(stream_documents_into_runs(dichro_model.add_run))
    return dichro_model, dichro_view
