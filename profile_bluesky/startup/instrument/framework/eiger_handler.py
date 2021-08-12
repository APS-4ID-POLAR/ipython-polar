""" 
Handler for EIGER files.

+ Have to modify the one from eiger_io because that one expects the file name
to be '{}_{}_master.h5'.format(self._base_path, seq_id).
"""

from eiger_io.fs_handler_dask import (
    EigerHandlerDask, PIMSDask, EIGER_MD_LAYOUT
)
import h5py
import dask.array as da


def _load_eiger_images(master_path):
    ''' load images from EIGER data using fpath.
        This separation is made from the handler to allow for some code that unfortunately depended
            on this step. (which used to be in EigerImages)
        master_path : the full filename of the path
    '''
    with h5py.File(master_path, 'r') as f:
        try:
            # Eiger firmware v1.3.0 and onwards
            _entry = f['entry']['data']
        except KeyError:
            _entry = f['entry']          # Older firmwares
    
        # TODO : perhaps remove the metadata eventually
        md = dict()
        md = {k: f[v][()] for k, v in EIGER_MD_LAYOUT.items()}
        # the pixel mask from the eiger contains:
        # 1  -- gap
        # 2  -- dead
        # 4  -- under-responsive
        # 8  -- over-responsive
        # 16 -- noisy
        pixel_mask = md['pixel_mask']
        md['binary_mask'] = (pixel_mask == 0)
        md['framerate'] = 1./md['frame_time']
    
        # TODO : Return a multi-dimensional PIMS seq.
        # this is the logic that creates the linked dask array
        elements = list()
        key_names = sorted(list(_entry.keys()))
        for keyname in key_names:
            #print(f"{keyname}")
            val = _entry[keyname]
            elements.append(da.from_array(val, chunks=val.chunks))
    
        res = da.concatenate(elements)

    return res, md


class MyEigerHandlerDask(EigerHandlerDask):
    
    # this is on a per event level
    # Left seq_id in args because it will probably break something else...
    def __call__(self, seq_id, frame_num=None):
        master_path = '{}_master.h5'.format(self._base_path)

        data, md = _load_eiger_images(master_path)
        # PIMS subclass using Dask
        # this gives metadata and also makes the assumption when
        # to run .compute() for dask array
        ret = PIMSDask(data, md=md)
        if frame_num is not None:
            ret = ret[frame_num]
        return ret

    def get_file_list(self, datum_kwargs):
        ''' get the file list.
            Receives a list of datum_kwargs for each datum
        '''
        filenames = []
        for dm_kw in datum_kwargs:
            filename = '{}_master.h5'.format(self._base_path)
            filenames.append(filename)

        return filenames
