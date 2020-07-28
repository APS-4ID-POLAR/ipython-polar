# mono = EpicsMotor('4idb:m1', name='mono', labels=('motor',))  # Kohzu Theta # home_slew_rate=0
# mon_y = EpicsMotor('4idb:m2', name='mon_y', labels=('motor',))  # Kohzu Y2
# # 2: MOT002 =    NONE:0/3   2000  1  2000  200   50  125    0 0x003    mon_z  Kohzu Z2  # Kohzu Z2
# mon_thf = EpicsMotor('4idb:m4', name='mon_thf', labels=('motor',))  # Kohzu Th2f
# mon_chi = EpicsMotor('4idb:m5', name='mon_chi', labels=('motor',))  # Kohzu Chi
# th = EpicsMotor('4iddx:m65', name='th', labels=('motor',))  # Theta # slop=2
# tth = EpicsMotor('4iddx:m66', name='tth', labels=('motor',))  # Two Theta
# th = EpicsMotor('4iddx:m65', name='th', labels=('motor',))  # 4C Theta
# tth = EpicsMotor('4iddx:m66', name='tth', labels=('motor',))  # 4C Two Theta
# eta = EpicsMotor('4iddx:m65', name='eta', labels=('motor',))  # PSIC-ETA
# del = EpicsMotor('4iddx:m66', name='del', labels=('motor',))  # PSIC-Delta
# phi = EpicsMotor('4iddx:m68', name='phi', labels=('motor',))  # Phi
# chi = EpicsMotor('4iddx:m67', name='chi', labels=('motor',))  # Chi
# bth = EpicsMotor('4iddx:m69', name='bth', labels=('motor',))  # Base Th
# btth = EpicsMotor('4iddx:m70', name='btth', labels=('motor',))  # Base tth
# mu = EpicsMotor('4iddx:m69', name='mu', labels=('motor',))  # PSIC-MU
# nu = EpicsMotor('4iddx:m70', name='nu', labels=('motor',))  # PSIC-NU
# hcirc = EpicsMotor('4iddx:m18', name='hcirc', labels=('motor',))  # 8C horiz
# vcirc = EpicsMotor('4iddx:m17', name='vcirc', labels=('motor',))  # 8C verical
# ath = EpicsMotor('4iddx:m77', name='ath', labels=('motor',))  # Ana Theta
# achi = EpicsMotor('4iddx:m79', name='achi', labels=('motor',))  # Ana Chi
# atth = EpicsMotor('4iddx:m78', name='atth', labels=('motor',))  # Ana 2Theta
# cryox = EpicsMotor('4iddx:m14', name='cryox', labels=('motor',))  # Cryo X
# cryoy = EpicsMotor('4iddx:m15', name='cryoy', labels=('motor',))  # Cryo Y
# cryoz = EpicsMotor('4iddx:m16', name='cryoz', labels=('motor',))  # Cryo Z
# pr1x = EpicsMotor('4idb:m10', name='pr1x', labels=('motor',))  # PhaseR1 X
# pr1y = EpicsMotor('4idb:m11', name='pr1y', labels=('motor',))  # PhaseR1 Y
# pr1th = EpicsMotor('4idb:m13', name='pr1th', labels=('motor',))  # PhaseR1 Th
# pr2x = EpicsMotor('4idb:m15', name='pr2x', labels=('motor',))  # PhasR2 X
# pr2y = EpicsMotor('4idb:m16', name='pr2y', labels=('motor',))  # PhasR2 Y
# pr2th = EpicsMotor('4idb:m18', name='pr2th', labels=('motor',))  # PhasR2 Th
# pr3x = EpicsMotor('4idb:m19', name='pr3x', labels=('motor',))  # PhasR3 X
# pr3y = EpicsMotor('4idb:m20', name='pr3y', labels=('motor',))  # PhasR3 Y
# pr3th = EpicsMotor('4idb:m21', name='pr3th', labels=('motor',))  # PhasR3 Th
# uptaby = EpicsMotor('4iddx:m10', name='uptaby', labels=('motor',))  # Uptable Y
mtop = EpicsMotor('4iddx:m61', name='mtop', labels=('motor',))  # MagGrdTop
mbot = EpicsMotor('4iddx:m62', name='mbot', labels=('motor',))  # MagGrdBot
# ciatra = EpicsMotor('4iddx:m63', name='ciatra', labels=('motor',))  # CIATRA
minb = EpicsMotor('4iddx:m64', name='minb', labels=('motor',))  # MagGrdInb
# magz = EpicsMotor('4iddx:m51', name='magz', labels=('motor',))  # AMIMagnetZ
# magx = EpicsMotor('4iddx:m52', name='magx', labels=('motor',))  # AMIMagenetX
osx = EpicsMotor('4iddx:m12', name='osx', labels=('motor',))  # OSA X
osy = EpicsMotor('4iddx:m13', name='osy', labels=('motor',))  # OSA Y
hpsmx = EpicsMotor('4iddx:m46', name='hpsmx', labels=('motor',))  # HP Samp X
hpsmy = EpicsMotor('4iddx:m47', name='hpsmy', labels=('motor',))  # HP Samp Y
hpsmr = EpicsMotor('4iddx:m48', name='hpsmr', labels=('motor',))  # HP Samp Rot
smagx = EpicsMotor('4iddx:m43', name='smagx', labels=('motor',))  # 2Tmag X
smagy = EpicsMotor('4iddx:m44', name='smagy', labels=('motor',))  # 2Tmag Y
smagrot = EpicsMotor('4iddx:m45', name='smagrot', labels=('motor',))  # 2Tmag Rot
# mrot = EpicsMotor('4iddx:m53', name='mrot', labels=('motor',))  # 4T Mag Th
# mtabx = EpicsMotor('4iddx:m49', name='mtabx', labels=('motor',))  # 4T MagTab X
# mtaby = EpicsMotor('4iddx:m50', name='mtaby', labels=('motor',))  # 4T MagTab Y
dvgap = EpicsMotor('4iddx:m21', name='dvgap', labels=('motor',))  # MagVGap
dvcen = EpicsMotor('4iddx:m22', name='dvcen', labels=('motor',))  # MagVCen
dhgap = EpicsMotor('4iddx:m24', name='dhgap', labels=('motor',))  # MagHGap
dhcen = EpicsMotor('4iddx:m23', name='dhcen', labels=('motor',))  # MagHCen
# kbicx = EpicsMotor('4iddx:m33', name='kbicx', labels=('motor',))  # KB IC X
lofff = EpicsMotor('4id:sm6', name='lofff', labels=('motor',))  # LockOff
qbpm = EpicsMotor('4idb:m31', name='qbpm', labels=('motor',))  # Quad-BPM
sltvcen = EpicsMotor('4iddx:m40', name='sltvcen', labels=('motor',))  # 8CslitIn-Vcen
# kbicy = EpicsMotor('4iddx:m34', name='kbicy', labels=('motor',))  # KB IC Y
mirxu = EpicsMotor('4idb:m37', name='mirxu', labels=('motor',))  # flat mir up
mirxd = EpicsMotor('4idb:m38', name='mirxd', labels=('motor',))  # flat mir dow
# mphi = EpicsMotor('4iddx:m56', name='mphi', labels=('motor',))  # AMIMagnetPhi
mirry = EpicsMotor('4id:sm8', name='mirry', labels=('motor',))  # MirrorY
vory = EpicsMotor('4iddx:m35', name='vory', labels=('motor',))  # VortexY
vorx = EpicsMotor('4iddx:m36', name='vorx', labels=('motor',))  # VortexX
# uptabx = EpicsMotor('4iddx:m9', name='uptabx', labels=('motor',))  # Uptab X
# ciarot = EpicsMotor('4iddx:m58', name='ciarot', labels=('motor',))  # CIA ROT
# xbpmx = EpicsMotor('4iddx:m19', name='xbpmx', labels=('motor',))  # XBPM hor
# xbpmy = EpicsMotor('4iddx:m20', name='xbpmy', labels=('motor',))  # XBPM ver
# scaler1 = ScalerCH('4id:scaler1', name='scaler1', labels=('detectors',))
# counter: sec = SpecCounter(mne='sec', config_line='0', name='Seconds', unit='0', chan='0', pvname=4id:scaler1.S1)
# counter: ic1 = SpecCounter(mne='ic1', config_line='1', name='IC1', unit='0', chan='1', pvname=4id:scaler1.S2)
# counter: ic2 = SpecCounter(mne='ic2', config_line='2', name='IC2', unit='0', chan='2', pvname=4id:scaler1.S3) # misc_par_2=0
# counter: ic3 = SpecCounter(mne='ic3', config_line='3', name='IC3', unit='0', chan='3', pvname=4id:scaler1.S4)
# ic4 = EpicsSignal('4id:scaler1currentAI', name='ic4', labels=('detectors',))
# counter: ic5 = SpecCounter(mne='ic5', config_line='5', name='IC5', unit='0', chan='5', pvname=4id:scaler1.S6)
# counter: cyber8c = SpecCounter(mne='cyber8c', config_line='6', name='Cyber8C', unit='0', chan='6', pvname=4id:scaler1.S7)
# counter: cyberm = SpecCounter(mne='cyberm', config_line='7', name='CyberMag', unit='0', chan='7', pvname=4id:scaler1.S8)
# counter: yapicr = SpecCounter(mne='yapicr', config_line='8', name='AP/ICR', unit='0', chan='8', pvname=4id:scaler1.S9)
# counter: apd = SpecCounter(mne='apd', config_line='9', name='APD', unit='0', chan='9', pvname=4id:scaler1.S10)
# counter: sca1 = SpecCounter(mne='sca1', config_line='10', name='Sca1', unit='0', chan='10', pvname=4id:scaler1.S11)
# counter: sca2 = SpecCounter(mne='sca2', config_line='11', name='SCA2', unit='0', chan='11', pvname=4id:scaler1.S12)
# counter: photo = SpecCounter(mne='photo', config_line='12', name='PhotoDiode', unit='0', chan='12', pvname=4id:scaler1.S13)
# counter: ldc = SpecCounter(mne='ldc', config_line='13', name='Lock DC', unit='0', chan='13', pvname=4id:scaler1.S14)
# counter: lac = SpecCounter(mne='lac', config_line='14', name='Lock AC', unit='0', chan='14', pvname=4id:scaler1.S15)
# counter: lacoff = SpecCounter(mne='lacoff', config_line='15', name='Lock ACoff', unit='0', chan='15', pvname=4id:scaler1.S16)
# 16: CNT016 =     NONE  2  2      1 0x000   lacfix  LockACfix
# 17: CNT017 =     NONE  3  1      1 0x000     dsum  DichroSum
# 18: CNT018 =     NONE  3  2      1 0x000    ddiff  DichroDiff
# 19: CNT019 =     NONE  3  3      1 0x000    dflip  DichroFlip
# 20: CNT020 =     NONE  3  4      1 0x000     dart  DichroArt
# iaps = EpicsSignal('S:SRcurrentAI', name='iaps', labels=('detectors',))  # Iaps
# 22: CNT022 =     NONE  3  4      1 0x000    spsum  SplitSum
# 23: CNT023 =     NONE  3  5      1 0x000    sppos  SplitPos
qsum = EpicsSignal('4id:userTran6.E', name='qsum', labels=('detectors',))  # QBPM Sum
qpos = EpicsSignal('4id:userTran6.G', name='qpos', labels=('detectors',))  # QBPM Pos
qsumh = EpicsSignal('4id:userTran6.H', name='qsumh', labels=('detectors',))  # QBPMH Sum
qposh = EpicsSignal('4id:userTran6.J', name='qposh', labels=('detectors',))  # QBPMH Pos
srs810x = EpicsSignal('4idd:SRS810:1:X.SVAL', name='srs810x', labels=('detectors',))  # SRS810x
srs810y = EpicsSignal('4idd:SRS810:1:Y.SVAL', name='srs810y', labels=('detectors',))  # SRS810y
# 30: CNT030 =     NONE  5  0      1 0x000  Filters  Filter
fld = EpicsSignal('4idd:LakeShore475:Fld.VAL', name='fld', labels=('detectors',))  # Hall
# 32: CNT032 =     NONE  5  2      1 0x000  scatot1  Scatot1
roi11 = EpicsSignal('4iddQuad:mca1.R0', name='roi11', labels=('detectors',))  # ROI11
roi12 = EpicsSignal('4iddQuad:mca1.R1', name='roi12', labels=('detectors',))  # ROI12
# hpol = EpicsSignal('4idb:scaler1.S2', name='hpol', labels=('detectors',))  # Hor Diode
# vpol = EpicsSignal('4idb:scaler1.S3', name='vpol', labels=('detectors',))  # Ver Diode
roi21 = EpicsSignal('4iddQuad:mca2.R0', name='roi21', labels=('detectors',))  # ROI21
roi22 = EpicsSignal('4iddQuad:mca2.R1', name='roi22', labels=('detectors',))  # ROI22
roi31 = EpicsSignal('4iddQuad:mca3.R0', name='roi31', labels=('detectors',))  # ROI31
roi32 = EpicsSignal('4iddQuad:mca3.R1', name='roi32', labels=('detectors',))  # ROI32
roi41 = EpicsSignal('4iddQuad:mca4.R0', name='roi41', labels=('detectors',))  # ROI41
roi42 = EpicsSignal('4iddQuad:mca4.R1', name='roi42', labels=('detectors',))  # ROI42
roi0 = EpicsSignal('4idd:mca1.R0', name='roi0', labels=('detectors',))  # ROI0
roi1 = EpicsSignal('4idd:mca1.R1', name='roi1', labels=('detectors',))  # ROI1
roi2 = EpicsSignal('4idd:mca1.R2', name='roi2', labels=('detectors',))  # ROI2
pil1 = EpicsSignal('dp_pixirad_xrd74:Stats1:Total_RBV', name='pil1', labels=('detectors',))
pil2 = EpicsSignal('dp_pixirad_xrd74:Stats2:Total_RBV', name='pil2', labels=('detectors',))
dtm = EpicsSignal('4idd:DTM:measField', name='dtm', labels=('detectors',))  # dtmgaus
# 49: CNT049 =     NONE  5  5      1 0x000  scatot2  Scatot2
icr1 = EpicsSignal('4iddQuad:dxp1:InputCountRate', name='icr1', labels=('detectors',))  # ICR1
icr2 = EpicsSignal('4iddQuad:dxp2:InputCountRate', name='icr2', labels=('detectors',))  # ICR2
icr3 = EpicsSignal('4iddQuad:dxp3:InputCountRate', name='icr3', labels=('detectors',))  # ICR3
icr4 = EpicsSignal('4iddQuad:dxp4:InputCountRate', name='icr4', labels=('detectors',))  # ICR4
ocr1 = EpicsSignal('4iddQuad:dxp1:OutputCountRate', name='ocr1', labels=('detectors',))  # OCR1
ocr2 = EpicsSignal('4iddQuad:dxp2:OutputCountRate', name='ocr2', labels=('detectors',))  # OCR2
ocr3 = EpicsSignal('4iddQuad:dxp3:OutputCountRate', name='ocr3', labels=('detectors',))  # OCR3
ocr4 = EpicsSignal('4iddQuad:dxp4:OutputCountRate', name='ocr4', labels=('detectors',))  # OCR4
# 58: CNT058 =     NONE  5  6      1 0x000    sca1c  Scatot1c
# 59: CNT059 =     NONE  5  7      1 0x000    sca2c  Scatot2c
icr = EpicsSignal('4idd:dxp1:InputCountRate', name='icr', labels=('detectors',))  # ICR
ocr = EpicsSignal('4idd:dxp1:OutputCountRate', name='ocr', labels=('detectors',))  # OCR
# 62: CNT062 =     NONE  5  8      1 0x000    roi0c  ROI0c
# 63: CNT063 =     NONE  5  9      1 0x000    roi1c  ROI1c
# 64: CNT064 =     NONE 10  4      1 0x000    imtot  imtot
# 65: CNT065 =     NONE 10  5      1 0x000    immax  immax
# 66: CNT066 =     NONE 11  0      1 0x000   imroi1  imroi1
# 67: CNT067 =     NONE 11  1      1 0x000   imroi2  imroi2
# 68: CNT068 =     NONE 11  2      1 0x000   imroi3  imroi3
# 69: CNT069 =     NONE 11  3      1 0x000   imroi4  imroi4
# 70: CNT070 =     NONE 11  4      1 0x000   imsca1  imsca1
# 71: CNT071 =     NONE 11  5      1 0x000   imsca2  imsca2
# 72: CNT072 =     NONE 12  0      1 0x000   imsca3  imsca3
# 73: CNT073 =     NONE 12  1      1 0x000   imsca4  imsca4
# 74: CNT074 =     NONE 12  2      1 0x000   transm  trasm
# 75: CNT075 =     NONE 12  3      1 0x000  filterm  filtermask
# 76: CNT076 =     NONE 12  4      1 0x000  corrdet  corrdet
# 77: CNT077 =     NONE 12  5      1 0x000  scanbar  scan_bar
i0h0c0 = EpicsSignal('4id:scaler3.S2', name='i0h0c0', labels=('detectors',))  # I0_H0C0
i0h0c1 = EpicsSignal('4id:scaler3.S3', name='i0h0c1', labels=('detectors',))  # I0_H0C1
i0h1c0 = EpicsSignal('4id:scaler3.S4', name='i0h1c0', labels=('detectors',))  # I0_H1C0
i0h1c1 = EpicsSignal('4id:scaler3.S5', name='i0h1c1', labels=('detectors',))  # I0_H1C1
i1h0c0 = EpicsSignal('4id:scaler3.S6', name='i1h0c0', labels=('detectors',))  # I1_H0C0
i1h0c1 = EpicsSignal('4id:scaler3.S7', name='i1h0c1', labels=('detectors',))  # I1_H0C1
i1h1c0 = EpicsSignal('4id:scaler3.S8', name='i1h1c0', labels=('detectors',))  # I1_H1C0
i1h1c1 = EpicsSignal('4id:scaler3.S9', name='i1h1c1', labels=('detectors',))  # I1_H1C1
cl_h0c0 = EpicsSignal('4id:scaler3.S10', name='cl_h0c0', labels=('detectors',))  # Clock_H0C0
cl_h0c1 = EpicsSignal('4id:scaler3.S11', name='cl_h0c1', labels=('detectors',))  # Clock_H0C1
cl_h1c0 = EpicsSignal('4id:scaler3.S12', name='cl_h1c0', labels=('detectors',))  # Clock_H1C0
cl_h1c1 = EpicsSignal('4id:scaler3.S13', name='cl_h1c1', labels=('detectors',))  # Clock_H1C1
i0h0 = EpicsSignal('4id:softGlue:UpCntr-3_COUNTS', name='i0h0', labels=('detectors',))  # I0_H0
i0h1 = EpicsSignal('4id:softGlue:UpCntr-4_COUNTS', name='i0h1', labels=('detectors',))  # I0_H1
i1h0 = EpicsSignal('4id:softGlue:UpCntr-1_COUNTS', name='i1h0', labels=('detectors',))  # I1_H0
i1h1 = EpicsSignal('4id:softGlue:UpCntr-2_COUNTS', name='i1h1', labels=('detectors',))  # I1_H1
# 94: CNT094 =     NONE 12  6      1 0x000  diff_i1  I1_Diff
# 95: CNT095 =     NONE 12  7      1 0x000  diff_ch  XMCD_chop
sampT = EpicsSignal('4idd:LS336:TC3:IN2', name='sampT', labels=('detectors',))  # SampTemp
roi1c1 = EpicsSignal('S4QX4:MCA1ROI:1:Total_RBV', name='roi1c1', labels=('detectors',))  # xspRoi1Ch1
roi1c2 = EpicsSignal('S4QX4:MCA2ROI:1:Total_RBV', name='roi1c2', labels=('detectors',))  # xspRoi1Ch2
roi1c3 = EpicsSignal('S4QX4:MCA3ROI:1:Total_RBV', name='roi1c3', labels=('detectors',))  # xspRoi1Ch3
roi1c4 = EpicsSignal('S4QX4:MCA4ROI:1:Total_RBV', name='roi1c4', labels=('detectors',))  # xspRoi1Ch4
ocr1x = EpicsSignal('S4QX4:C1SCA4:Value_RBV', name='ocr1x', labels=('detectors',))  # xspOCR1
ocr2x = EpicsSignal('S4QX4:C2SCA4:Value_RBV', name='ocr2x', labels=('detectors',))  # xspOCR2
ocr3x = EpicsSignal('S4QX4:C3SCA4:Value_RBV', name='ocr3x', labels=('detectors',))  # xspOCR3
ocr4x = EpicsSignal('S4QX4:C4SCA4:Value_RBV', name='ocr4x', labels=('detectors',))  # xspOCR4
roi2c1 = EpicsSignal('S4QX4:MCA1ROI:2:Total_RBV', name='roi2c1', labels=('detectors',))  # xspRoi2Ch1
roi2c2 = EpicsSignal('S4QX4:MCA2ROI:2:Total_RBV', name='roi2c2', labels=('detectors',))  # xspRoi2Ch2
roi2c3 = EpicsSignal('S4QX4:MCA3ROI:2:Total_RBV', name='roi2c3', labels=('detectors',))  # xspRoi2Ch3
roi2c4 = EpicsSignal('S4QX4:MCA4ROI:2:Total_RBV', name='roi2c4', labels=('detectors',))  # xspRoi2Ch4
xsp1DTc = EpicsSignal('S4QX4:C1SCA8:Value_RBV', name='xsp1DTc', labels=('detectors',))
xsp2DTc = EpicsSignal('S4QX4:C2SCA8:Value_RBV', name='xsp2DTc', labels=('detectors',))
xsp3DTc = EpicsSignal('S4QX4:C3SCA8:Value_RBV', name='xsp3DTc', labels=('detectors',))
xsp4DTc = EpicsSignal('S4QX4:C4SCA8:Value_RBV', name='xsp4DTc', labels=('detectors',))
# 113: CNT113 =     NONE  8 16      1 0x000    xspt1  xspRoi1tot
# 114: CNT114 =     NONE  8 17      1 0x000   xspt1c  xspRoi1totc # misc_par_2=Value_RBV
# 115: CNT115 =     NONE  8 18      1 0x000  xspt1cM  xspRoi1totcMon # misc_par_2=Value_RBV
# 116: CNT116 =     NONE  8 19      1 0x000  xspt2cM  xspRoi2totcMon # misc_par_2=Value_RBV
# 117: CNT117 =     NONE  8 20      1 0x000   xspt1M  xspRoi1totMon
keithV = EpicsSignal('4idd:K24K:measVoltAI', name='keithV', labels=('detectors',))
mcsA = EpicsSignal('4id:userCalc7.I', name='mcsA', labels=('detectors',))
mcsB = EpicsSignal('4id:userCalc7.J', name='mcsB', labels=('detectors',))
mcsAerr = EpicsSignal('4id:userCalc7.K', name='mcsAerr', labels=('detectors',))
xbpmX = EpicsSignal('4iddMZ0:TetrAMM:PosX:MeanValue_RBV', name='xbpmX', labels=('detectors',))
xbpmY = EpicsSignal('4iddMZ0:TetrAMM:PosY:MeanValue_RBV', name='xbpmY', labels=('detectors',))
xbpm1 = EpicsSignal('4iddMZ0:TetrAMM:Current1:MeanValue_RBV', name='xbpm1', labels=('detectors',))
xbpm2 = EpicsSignal('4iddMZ0:TetrAMM:Current2:MeanValue_RBV', name='xbpm2', labels=('detectors',))
xbpm3 = EpicsSignal('4iddMZ0:TetrAMM:Current3:MeanValue_RBV', name='xbpm3', labels=('detectors',))
xbpm4 = EpicsSignal('4iddMZ0:TetrAMM:Current4:MeanValue_RBV', name='xbpm4', labels=('detectors',))
