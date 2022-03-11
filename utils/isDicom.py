import string

def isDicom(filePath: string):
    if filePath.endswith(".dcm"):
        return True
    else:
        with open(filePath,"rb") as f:
            f.seek(128,1)
            strb = f.read(4)
            return strb == b'DICM'
# E:\research\MRViewer_test\Patient_Test_data\MRIDicom_for_download_1\gre_scout_20200725_150825\00000001