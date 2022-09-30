"""
Create new stream with processed XMCD data
"""

from bluesky.callbacks.stream import LiveDispatcher
from streamz import Source
from numpy import mean, log, array


class Settings():
    positioner = "energy"
    monitor = "Ion Ch 4"
    detector = "Ion Ch 5"
    transmission = True


dichro_settings = Settings()


# TODO: Should this go in the pr_setup?
class DichroStream(LiveDispatcher):
    """Stream that processes XMCD and XANES"""
    def __init__(self, settings=dichro_settings, n=4):
        self.n = n
        self.in_node = None
        self.out_node = None
        self.processor = None
        self.data_keys = None
        self.settings = settings
        self._trigger = False
        super().__init__()

    def start(self, doc):
        """
        Create the stream after seeing the start document

        The callback looks for the 'average' key in the start document to
        configure itself.
        """
        # Grab the average key
        # We could have something like this, but likely will never use it.
        # self.n = doc.get('average', self.n)

        # Define our nodes
        if not self.in_node:
            self.in_node = Source(stream_name='dichro_xmcd')

        self.processor = self.in_node.partition(self.n)

        self.data_keys = [
            self.settings.positioner,
            self.settings.monitor,
            self.settings.detector,
        ]

        def process_xmcd(cache):
            processed_evt = dict()
            desc_id = cache[0]['descriptor']

            # Check that all of our events came from the same configuration
            if not all([desc_id == evt['descriptor'] for evt in cache]):
                raise Exception(
                    'The events in this bundle are from different'
                    'configurations!'
                )

            # Use the last descriptor to avoid strings and objects
            if all([key in self.raw_descriptors[desc_id]['data_keys'] for key
                    in self.data_keys]):
                processed_evt[self.data_keys[0]] = mean(
                    [evt['data'][self.data_keys[0]] for evt in cache], axis=0
                )

                _mon = array(
                    [evt['data'][self.data_keys[1]] for evt in cache]
                )

                _det = array(
                    [evt['data'][self.data_keys[2]] for evt in cache]
                )

                _xas = (
                    log(_mon/_det) if self.settings.transmission else _det/_mon
                )

                processed_evt["xas"] = mean(_xas)
                processed_evt["xmcd"] = (
                    ((_xas[0] + _xas[3]) - (_xas[1] + _xas[2]))/4
                )
            else:
                raise Exception(
                    'The input data keys do not match entries in the database.'
                )

            return {'data': processed_evt, 'descriptor': desc_id}

        self.out_node = self.processor.map(process_xmcd)
        self.out_node.sink(self.process_event)
        super().start(doc)

    def event(self, doc):
        """Send an Event through the stream"""
        descriptor = self.raw_descriptors[doc["descriptor"]]
        if descriptor.get("name") == "primary":
            self.in_node.emit(doc)

    def stop(self, doc):
        """Delete the stream when run stops"""
        self.in_node = None
        self.out_node = None
        self.processor = None
        self.data_keys = None
        self._trigger = False
        super().stop(doc)
