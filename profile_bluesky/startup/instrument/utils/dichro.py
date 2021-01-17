
from ..callbacks.dichro_plot import AutoDichroPlot
from bluesky_widgets.qt.figures import QtFigures
from bluesky_widgets.utils.streaming import stream_documents_into_runs
from ..framework import RE

__all__ = ["dichro_model", "dichro_view"]


# Add dichro plot to RE
dichro_model = AutoDichroPlot()
dichro_view = QtFigures(dichro_model.figures)
dichro_view.show()
RE.subscribe(stream_documents_into_runs(dichro_model.add_run))
