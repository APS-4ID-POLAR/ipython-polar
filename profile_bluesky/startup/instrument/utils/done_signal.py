
__all__ = ['DoneSignal']

from ophyd import Signal

class DoneSignal(Signal):
    def get(self,**kwargs):
        readback = self.parent.readback.get()
        setpoint = self.parent.setpoint.get()
        tolerance = self.parent.tolerance

        if abs(readback-setpoint) <= tolerance:
            self.put(1)
        else:
            self.put(0)

        return self._readback
