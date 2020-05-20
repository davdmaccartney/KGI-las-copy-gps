import os
import numpy as np
from laspy.file import File
import time
import easygui
from imutils import paths
import fnmatch
import sys
import pandas as pd
from timeit import default_timer as timer


#pd.options.display.float_format = '{:.6f}'.format

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def update_progress(progress):
    barLength = 30 # Modify this to change the length of the progress bar
    
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% ".format( "#"*block + "-"*(barLength-block), int(progress*100))
    sys.stdout.write(text)
    sys.stdout.flush()




dirname1 = easygui.diropenbox(msg=None, title="Please select the target directory", default=None )
total_con=len(fnmatch.filter(os.listdir(dirname1), '*.las'))
D1 = str(total_con)
msg = str(total_con) +" files do you want to continue?"
title = "Please Confirm"
if easygui.ynbox(msg, title, ('Yes', 'No')): # show a Continue/Cancel dialog
    pass # user chose Continue else: # user chose Cancel
else:
    exit(0)

dirname2 = easygui.diropenbox(msg=None, title="Please select the source to copy from", default=None )
total_con=len(fnmatch.filter(os.listdir(dirname2), '*.las'))
D2 = str(total_con)
msg = str(total_con) +" files do you want to continue?"
title = "Please Confirm"
if easygui.ynbox(msg, title, ('Yes', 'No')): # show a Continue/Cancel dialog
    pass # user chose Continue else: # user chose Cancel
else:
    exit(0)

   
file_Dir1 = os.path.basename(dirname1)
file_Dir2 = os.path.basename(dirname2)

if dirname1 == dirname2:
   easygui.msgbox('The process will end same folder to compare')
   exit(0)

if D1 != D2:
   easygui.msgbox('The process will end not same number of files')
   exit(0)


dirout = os.path.join(dirname1,"new_lidar")
if not os.path.exists(dirout):
    os.mkdir(dirout)
ci=0
cls()
eR=0



for filename in os.listdir(dirname1):
     if filename.endswith(".las"):
        ci  += 1
        # Reading LiDAR
        start = timer()
        inFile1 = File(dirname1+'\\'+filename, mode='r')
        
        try:
           inFile2 = File(dirname2+'\\'+filename, mode='r')


        except OSError:
           easygui.msgbox('No file:'+filename+' in :'+dirname2+' the process will end')
           sys.exit(0) 

        # aligne offet of the source to the target
        hXori = inFile1.header.offset[0]
        hYori = inFile1.header.offset[1]
        hZori = inFile1.header.offset[2]
        hSori = inFile1.header.scale[0]
        
        hXsrc = inFile2.header.offset[0]
        hYsrc = inFile2.header.offset[1]
        hZsrc = inFile2.header.offset[2]
        hSsrc = inFile2.header.scale[0]
            

        point_copy_ori = inFile1.points.copy()
        hXdif=0
        hYdif=0
        hZdif=0

        if (hXori != hXsrc):
          hXdif = int((hXsrc-hXori)/hSori)

        if (hYori != hYsrc):
          hYdif = int((hYsrc-hYori)/hSori)

        if (hZori != hZsrc):
          hZdif = int((hZsrc-hZori)/hSori)

        #print(hXdif, hYdif, hZdif)
        class1_points = inFile1.points
        class2_points = inFile2.points

        ori = pd.DataFrame(np.empty(0, dtype=[('X',np.int32),('Y',np.int32),('Z',np.int32),('intensity',np.int),('flag_byte',np.int),('angle',np.ubyte)]))
        src = pd.DataFrame(np.empty(0, dtype=[('X',np.int32),('Y',np.int32),('Z',np.int32),('intensity',np.int),('flag_byte',np.int),('angle',np.ubyte),('gps_timeT',np.int32)]))


        ori['X'] = (class1_points['point']['X'])
        ori['Y'] = (class1_points['point']['Y'])
        ori['Z'] = (class1_points['point']['Z'])       
        ori['intensity'] = (class1_points['point']['intensity'])
        ori['flag_byte'] = (class1_points['point']['flag_byte'])
        ori['angle'] = (class1_points['point']['scan_angle_rank'])

        src['X'] = (inFile2.X)+hXdif
        src['Y'] = (inFile2.Y)+hYdif
        src['Z'] = (inFile2.Z)+hZdif
        src['gps_timeT'] = (inFile2.gps_time)
        src['intensity'] = (inFile2.intensity)
        src['flag_byte'] = (inFile2.flag_byte)
        src['angle'] = (inFile2.scan_angle_rank)


        # drop source duplicate rows
        src.drop_duplicates(subset =['X','Y','Z','intensity','flag_byte','angle'], keep=False,inplace=True)

        # merge the dataframes on a left join style
        res = pd.merge(ori, src, on=['X','Y','Z','intensity','flag_byte','angle'], how='left')  


        del res['X']
        del res['Y']
        del res['Z']
        del res['intensity']
        del res['flag_byte']
        del res['angle']
                    

        # Writing the new las

        for row in res.itertuples():
               point_copy_ori[row.Index]['point']['gps_time']=row.gps_timeT
   
        
        
        outFile1 = File(dirout+'\\'+filename, mode = "w", header = inFile1.header)
        outFile1.points = point_copy_ori
        outFile1.close()
        



        inFile1.close()
        inFile2.close()
        update_progress(ci/int(D1))

 
if eR>0:
   print('Process finnihed :'+str(eR)+' errors read Comp-result.txt in the source folder')
else:
   print('Process finnihed with no errors')
   

exit(0)