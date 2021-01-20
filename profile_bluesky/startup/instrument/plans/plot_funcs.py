""" Generate plots """"

from ..session_logs import logger
logger.info(__file__)

__all__ = ['start_dichro_plot']

from bluesky_widgets.qt.figures import QtFigures
from bluesky_widgets.utils.streaming import stream_documents_into_runs
from ..framework import RE
from ..callbacks import AutoDichroPlot


def start_dichro_plot():

    global dichro_model
    global dichro_view

    dichro_model = AutoDichroPlot()
    dichro_view = QtFigures(dichro_model.figures)
    dichro_view.show()
    RE.subscribe(stream_documents_into_runs(dichro_model.add_run))

