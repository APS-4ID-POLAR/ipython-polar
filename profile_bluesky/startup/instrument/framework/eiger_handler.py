"""
Modified Eiger handler -> APS seems to use a different file naming.
"""
from glob import glob
from pathlib import Path
import dask.array
import h5py
from area_detector_handlers.eiger import EigerHandler


class MyEigerHandler(EigerHandler):

    def __call__(self, image_num):
        '''
        This returns data contained in the file.

        Parameters
        ----------
        image_num int
            Image number as read from eiger.cam.num_images_counter
        Returns
        -------
            A dask array
        '''

        fpath = Path(
            f'{self._file_prefix}_data_'
            f'{1 + (image_num // self._images_per_file):06d}.h5'
        ).absolute()

        try:
            file = self._files[fpath]
        except KeyError:
            file = h5py.File(fpath, 'r')
            self._files[fpath] = file

        da = dask.array.from_array(file['entry/data/data'])[
            image_num % self._images_per_file
        ]

        return da.reshape((1,) + da.shape)

    def get_file_list(self, datum_kwargs_gen):
        '''
        Get the file list.
        Receives a list of datum_kwargs for each datum.
        '''
        filenames = []
        for dm_kw in datum_kwargs_gen:
            new_filenames = glob(f'{self._file_prefix}_*')
            filenames.extend(new_filenames)

        return filenames
