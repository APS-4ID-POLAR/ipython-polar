from apstools.devices import PVPositionerSoftDoneWithStop as PVPos


class PVPositionerSoftDoneWithStop(PVPos):
    def _setup_move(self, position):
        self.cb_setpoint()
        super()._setup_move(position)
