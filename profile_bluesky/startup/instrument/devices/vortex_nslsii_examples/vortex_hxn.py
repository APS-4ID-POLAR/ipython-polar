from ophyd.device import (Component as Cpt)

from hxntools.detectors.xspress3 import (Xspress3FileStore,
                                         Xspress3Channel)
from hxntools.detectors.hxn_xspress3 import HxnXspress3DetectorBase
import threading
from ophyd import DeviceStatus

class HxnXspress3Detector(HxnXspress3DetectorBase):
    channel1 = Cpt(Xspress3Channel, 'C1_', channel_num=1)
    channel2 = Cpt(Xspress3Channel, 'C2_', channel_num=2)
    channel3 = Cpt(Xspress3Channel, 'C3_', channel_num=3)
    # Currently only using three channels. Uncomment these to enable more
    # channels:
    # channel4 = C(Xspress3Channel, 'C4_', channel_num=4)
    # channel5 = C(Xspress3Channel, 'C5_', channel_num=5)
    # channel6 = C(Xspress3Channel, 'C6_', channel_num=6)
    # channel7 = C(Xspress3Channel, 'C7_', channel_num=7)
    # channel8 = C(Xspress3Channel, 'C8_', channel_num=8)

    hdf5 = Cpt(Xspress3FileStore, 'HDF5:',
               write_path_template='/data/%Y/%m/%d/',
               mds_key_format='xspress3_ch{chan}',
               reg=db.reg,
               root='/data',
               )

    def __init__(self, prefix, *, configuration_attrs=None, read_attrs=None,
                 **kwargs):
        if configuration_attrs is None:
            configuration_attrs = ['external_trig', 'total_points',
                                   'spectra_per_point']
        if read_attrs is None:
            read_attrs = ['channel1', 'channel2', 'channel3', 'hdf5']
        super().__init__(prefix, configuration_attrs=configuration_attrs,
                         read_attrs=read_attrs, **kwargs)
        self._dispatch_cid = None
        self._spec_saved = threading.Event()


    def stage(self, *args, **kwargs):
        for j in itertools.count():
            try:
                ret = super().stage(*args, **kwargs)
            except TimeoutError:
                N_try = 20
                if j < 20:
                    print(f"failed to stage on try{j}/{N_try}, may try again")
                    continue
                else:
                    raise
            else:
                break


        # clear any existing callback
        if self._dispatch_cid is not None:
            self.hdf5.num_captured.clear_sub(self._dispatch_cid)
            self._dispatch_cid = None


        # always install the callback
        def _handle_spectrum_capture(old_value, value, timestamp, **kwargs):
            # if we get called and we are in fly mode, rip self off and bail
            # the flyscan takes care of this its self, but does not tell us we are in fly
            # mode until after we are staged
            if self.mode_settings.scan_type.get() != 'step':
                if self._dispatch_cid is not None:
                    self.hdf5.num_captured.clear_sub(self._dispatch_cid)
                    self._dispatch_cid = None
                return
            # grab the time and the previous value from the callback payload
            trigger_time = timestamp
            self._abs_trigger_count = old_value
            # dispatch for all of the channels
            for sn in self.read_attrs:
                if sn.startswith('channel') and '.' not in sn:
                    ch = getattr(self, sn)
                    self.dispatch(ch.name, trigger_time)
                    #print(ch.name, trigger_time, self._abs_trigger_count)

            self._abs_trigger_count = value
            self._spec_saved.set()

        # do the actual subscribe
        self._dispatch_cid = self.hdf5.num_captured.subscribe(
            _handle_spectrum_capture,
            run=False)

        return ret

    def trigger(self):
        self.sts = sts = DeviceStatus(self)
        # in the not step case, just return a done status object
        if self.mode_settings.scan_type.get() != 'step':
            sts._finished()
            return sts
        self._spec_saved.clear()

        def monitor():
            success = self._spec_saved.wait(60)
            sts._finished(success=success)

        # hold a ref for gc reasons
        self._th = threading.Thread(target=monitor)
        self._th.start()
        return sts


    def unstage(self, *args, **kwargs):

        try:
            if self._dispatch_cid is not None:
                self.hdf5.num_captured.clear_sub(self._dispatch_cid)
                self._dispatch_cid = None
        finally:
            import itertools
            for j in itertools.count():
                try:
                    ret = super().unstage(*args, **kwargs)
                except TimeoutError:
                    N_try = 20
                    if j < N_try:
                        print(f"failed to unstage on attempt {j}/{N_try}, may try again")
                        continue
                    else:
                        raise
                else:
                    break
            return ret




xspress3 = HxnXspress3Detector('XF:03IDC-ES{Xsp:1}:', name='xspress3')


# Create directories on the xspress3 server, otherwise scans can fail:
xspress3.make_directories.put(True)


elem_K_list = np.array(['Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf'])

energy_K_list = np.array([1040,1254,1487,1740,2011,2310,2622,2958,3314,3692,4093,4512,4953,5415,5900,6405,6931,7480,8046,8637,9251,9886,10543,11224,11924,12648,13396,14165,14958,15775,16615,17480,18367,19279,20216,21177,22163,23173,24210,25271,26359,27473,28612,29775,30973,32194,33442,55790,57535,59318,61141,63000,64896,66831,68806,70818,72872,74970,77107,79291,81516,83785,86106,88478,90884,34720,36027,37361,38725,40118,41542,42996,44482,45999,47547,49128,50742,52388,54070,93351,95868,98440,101059,103734,106472,109271,112121,115032])

elem_L_list = np.array(['Zn_L','Ga_L','Ge_L','AS_L','Se_L','Br_L','Kr_L','Rb_L','Sr_L','Y_L','Zr_L','Nb_L','Mo_L','Tc_L','Ru_L','Rh_L','Pd_L','Ag_L','Cd_L','In_L','Sn_L','Sb_L','Te_L','I_L','Xe_L','Cs_L','Ba_L','La_L','Hf_L','Ta_L','W_L','Re_L','Os_L','Ir_L','Pt_L','Au_L','Hg_L','Tl_L','Pb_L','Bi_L','Po_L','At_L','Rn_L','Fr_L','Ra_L','Ac_L','Ce_L','Pr_L','Nd_L','Pm_L','Sm_L','Eu_L','Gd_L','Tb_L','Dy_L','Ho_L','Er_L','Tm_L','Yb_L','Lu_L','Th_L','Pa_L','U_L','Np_L','Pu_L','Am_L','Cm_L','Bk_L','Cf_L'])

energy_L_list = np.array([1012,1098,1186,1282,1379,1481,1585,1692,1806,1924,2044,2169,2292,2423,2558,2697,2838,2983,3133,3280,3444,3604,3768,3938,4110,4285,4467,4647,7899,8146,8398,8652,8911,9175,9442,9713,9989,10269,10551,10839,11131,11427,11727,12031,12339,12652,4839,5035,5228,5432,5633,5850,6053,6273,6498,6720,6949,7180,7416,7655,12968,13291,13614,13946,14282,14620,14961,15308,15660])

elem_M_list = np.array(['Hf_M','Ta_M','W_M','Re_M','Os_M','Ir_M','Pt_M','Au_M','Hg_M','Tl_M','Pb_M','Bi_M','Po_M','At_M','Rn_M','Fr_M','Ra_M','Ac_M','Ce_M','Pr_M','Nd_M','Pm_M','Sm_M','Eu_M','Gd_M','Tb_M','Dy_M','Ho_M','Er_M','Tm_M','Yb_M','Lu_M','Th_M','Pa_M','U_M','Np_M','Pu_M','Am_M','Cm_M','Bk_M','Cf_M'])

energy_M_list = np.array([1646,1712,1775,1840,1907,1976,2048,2118,2191,2267,2342,2418,2499,2577,2654,2732,2806,2900,884,927,979,1023,1078,1122,1181,1233,1284,1342,1404,1463,1526,1580,2990,3071,3164,3250,3339,3429,3525,3616,3709])


def xspress3_roi_setup():
    elem_list = np.array(['Si','I_L','W_L','Fe','Ni','Cr','Pt_L','Pb','Mn','Co','Cu','Ti','Au_L','Zr_L', 'La_L', 'Ta_L'])
    num_elem = np.size(elem_list)
    if num_elem > 16:
        num_elem = 16
    for channel in [xspress3.channel1, xspress3.channel2, xspress3.channel3]:
        for i in range(num_elem):
            if elem_list[i] in elem_K_list:
                energy = energy_K_list[elem_K_list == elem_list[i]]
            elif elem_list[i] in elem_L_list:
                energy = energy_L_list[elem_L_list == elem_list[i]]
            elif elem_list[i] in elem_M_list:
                energy = energy_M_list[elem_M_list == elem_list[i]]
            else:
                print(elem_list[i], 'is not defined.')
                break
            channel.set_roi(i+1, energy-150, energy+150, name=elem_list[i])


'''
def xspress3_roi_setup():
    for channel in [xspress3.channel1, xspress3.channel2, xspress3.channel3]:
        #channel.set_roi(1, 9300, 9600, name='Pt')
        channel.set_roi(1, 1590, 1890, name='Si')
        #channel.set_roi(2, 1898, 2198, name='Pt_M')
        #channel.set_roi(2, 2150, 2450, name='S')
        #channel.set_roi(2, 14000, 14300, name='Sr')
        #channel.set_roi(2, 3790, 4090, name='I')
        #channel.set_roi(2, 3850, 4140, name='Bi_M')
        #channel.set_roi(2, 3300, 3600, name='Sn')
        channel.set_roi(4, 8250, 8550, name='W')
        channel.set_roi(2, 4690, 4990, name='Ce')
        #channel.set_roi(3, 4150, 4450, name='Cs')
        #channel.set_roi(2, 2019, 2319, name='Nb')
        #channel.set_roi(3, 5700, 6000, name='Eu')
        channel.set_roi(3, 4360, 4660, name='Ti')
        #channel.set_roi(3, 6800, 7100, name='Er')
        #channel.set_roi(5, 4250, 4550, name='Ba')
        channel.set_roi(5, 4150, 4450, name='Cs')
        #channel.set_roi(3, 1970, 2270, name='Au_M')
        #channel.set_roi(4, 5750, 6050, name='Mn')
        #channel.set_roi(5, 2472, 2772, name='Cl')
        #channel.set_roi(5, 2200, 2500, name='Pb_M')
        #channel.set_roi(5, 2810, 3110, name='Ag')
        #channel.set_roi(5, 6780, 7080, name='Co')
        channel.set_roi(6, 3542, 3842, name='Ca')
        channel.set_roi(7, 3130, 3430, name='In')
        channel.set_roi(8, 5900, 6200, name='Gd')
        channel.set_roi(9, 5078, 5378, name='Nd')
        #channel.set_roi(9, 4800, 5100, name='V')
        #channel.set_roi(7, 1850, 2150, name='P')
        #channel.set_roi(8, 3000, 3300, name='Cd')
        channel.set_roi(10, 5270, 5570, name='Cr')
        #channel.set_roi(9, 3160, 3460, name='K')
        #channel.set_roi(10, 10400, 10700, name='Pb')
        #channel.set_roi(10, 3600, 3900, name='Te')
        #channel.set_roi(11, 9550, 9850, name='Au')
        channel.set_roi(11, 6250, 6550, name='Fe')
        channel.set_roi(12, 11050, 11350, name='Se')
        #channel.set_roi(13, 8487, 8787, name='Zn')
        channel.set_roi(13, 8000, 8300, name='Ta')
        channel.set_roi(14, 7330, 7630, name='Ni')
        #channel.set_roi(15, 7950, 8150, name='Cu')
        channel.set_roi(15, 9300, 9600, name='Pt')
        #channel.set_roi(16, 11775, 12075, name='Br')
        #channel.set_roi(16, 9736, 10036, name='Ge')
        # channel.set_roi(17, 8250, 8550, 'W')
        # channel.set_roi(18, 9600, 9750, 'Au')
        # channel.set_roi(19, 11500, 12500, 'EL')
        # channel.set_roi(20, 1900, 2000, 'Y')
        # channel.set_roi(15, 1340, 1640, name='Al')
        # channel.set_roi(22, 4360, 4660, 'Ti')
        # channel.set_roi(23, 4550, 4750, 'La')
        channel.set_roi(16, 9150, 9350, name='Ga')
    '''

try:
    print('Configuring Xspress3 ROIs...')
    xspress3_roi_setup()
    print('Done')
except KeyboardInterrupt:
    print('Xspress3 ROI configuration cancelled.')


def hint_xspress_element(elm):
    elm = elm.upper()
    xspress3.hints['fields'] = [f'Det{j}_{elm}' for j in (1, 2, 3)]


def configure_xspress3(sclr):
    sclr.configuration_attrs = sclr.component_names
    sclr.flyer_timestamps.kind = 'omitted'
    sclr.roi_data.kind = 'omitted'
    sclr.make_directories.kind = 'omitted'
    sclr.rewindable.kind = 'omitted'
    for k, chan in sclr.channels.items():
        chan.configuration_names.kind = 'config'
        chan.vis_enabled.kind = 'omitted'
        chan.rois.kind = 'normal'
        chan.rois.num_rois.kind = 'config'
        chan.name = chan.name.replace('annel', '')
        for n in chan.rois.component_names:
            if 'roi' in n and n != 'num_rois':
                roi = getattr(chan.rois, n)
                roi.kind = 'normal'
                roi.value.kind = 'normal'
                roi.value_sum.kind = 'omitted'
            else:
                attr = getattr(chan.rois, n)
                attr.kind = 'config'

configure_xspress3(xspress3)
