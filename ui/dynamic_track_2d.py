import copy
from pdb import main
import SimpleITK as sitk
from SimpleITK.SimpleITK import DiffeomorphicDemonsRegistrationFilter
import numpy as np
# import os
# import cv2
from numpy.lib.arraypad import pad
# import csv
# from preprocess import *
# import kcftracker
# import time
# from skimage import io, transform

def preprocess_normalization(img, min, max):
    norm_img = ((img-img.min())/(img.max()-img.min()))*(max-min) + min
    return norm_img


def find_next_point(window, origin_x, origin_y, tracker_size):
    # 找window中的最小值作为下一个点
    m = np.argmin(window)
    x, y = divmod(m, window.shape[1])
    x = origin_x - tracker_size + x
    y = origin_y - tracker_size + y           
    return x, y


def detect_probe(img, start_x, start_y):
    # img = preprocess_normalization(img, 0, 255).astype(np.uint8)
    tracker_size = 3
    label_array = copy.deepcopy(img)
    label_array[label_array<100] = 0  
    img[label_array==0] = 255
    tracker_window = img[start_x-tracker_size:start_x+tracker_size,start_y-tracker_size:start_y+tracker_size]
    x, y = find_next_point(tracker_window, start_x, start_y, tracker_size)
    return x, y, img

def detect_probe_v2(img, start_point_x, start_point_y, mean):
    img = preprocess_normalization(img, 0, 255).astype(np.uint8)
    tracker_size = 3   
    label_array = copy.deepcopy(img)
    label_array[label_array<100] = 0      
    img[label_array==0] = 255
    step = 2
    diff = 99999
    pre_mean = mean
    potential_locates = [(start_point_x, start_point_y),(start_point_x, start_point_y-step),(start_point_x-step, start_point_y-step),(start_point_x-step, start_point_y),(start_point_x-step, start_point_y+step),
                            (start_point_x, start_point_y+step),(start_point_x+step, start_point_y+step),(start_point_x+step, start_point_y),(start_point_x+step, start_point_y-step)]
    for potential in potential_locates:
        tracker_window = img[potential[0]-tracker_size:potential[0]+tracker_size,potential[1]-tracker_size:potential[1]+tracker_size]
        cur_mean = np.mean(tracker_window)
        if cur_mean - mean < diff:
            (x, y) = potential
            diff = cur_mean - mean
            pre_mean = cur_mean

    return x, y, pre_mean

def detect_probe_v3(img, start_point_x, start_point_y, mean):
    # img = preprocess_normalization(img, 0, 255).astype(np.uint8)
    tracker_size = 3   
    label_array = copy.deepcopy(img)
    label_array[label_array<100] = 0      
    img[label_array==0] = 255
    step = 2
    diff = 99999
    pre_mean = mean
    potential_locates = [(start_point_x, start_point_y),(start_point_x, start_point_y-step),(start_point_x-step, start_point_y-step),(start_point_x-step, start_point_y),(start_point_x-step, start_point_y+step),
                            (start_point_x, start_point_y+step),(start_point_x+step, start_point_y+step),(start_point_x+step, start_point_y),(start_point_x+step, start_point_y-step)]
    for potential in potential_locates:
        tracker_window = img[potential[0]-tracker_size:potential[0]+tracker_size,potential[1]-tracker_size:potential[1]+tracker_size]
        cur_mean = np.mean(tracker_window)
        if cur_mean - mean < diff:
            (x, y) = potential
            diff = cur_mean - mean
            pre_mean = cur_mean

    return x, y, pre_mean

def pci_tracking(img, start_point_x, start_point_y, mean, tracker_size, start):
    if start:
        tracker_window = img[start_point_x-tracker_size:start_point_x+tracker_size,start_point_y-tracker_size:start_point_y+tracker_size]
        mean = np.mean(tracker_window)
    else:
        start_point_x, start_point_y, mean = detect_probe_v2(img, start_point_x, start_point_y, mean)            

    return start_point_x, start_point_y, mean

def track_by_camshift(imgs, label_array):

    frame = imgs[0]
    r,h,c,w = 153,9,140,9
    track_window = (c,r,w,h)

    roi = frame[r:r+h, c:c+w]
    # hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(roi, np.array((90)), np.array((255)))
    roi_hist = cv2.calcHist([roi],[0],mask,[180],[0,180])
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
    # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )

    for img in imgs:
        frame = img
        cv2.imshow("frame", frame)
        img[label_array==0] = 0
        cv2.imshow("erode", img)                 
        dst = cv2.calcBackProject([img],[0],roi_hist,[0,180],1)
        # apply meanshift to get the new location
        ret, track_window = cv2.CamShift(dst, track_window, term_crit)
        # Draw it on image
        # meanshift    
        # x,y,w,h = track_window
        # img2 = cv2.rectangle(frame, (x,y), (x+w,y+h), 255,2)

        # camshift
        pts = cv2.boxPoints(ret)
        pts = np.int0(pts)
        img2 = cv2.polylines(frame,[pts],True, 255,2)
        cv2.imshow('img2',img2)
        cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    path = '../dynamic_2d_robot.nii.gz'
    rawdata = sitk.ReadImage(path)
    data = sitk.GetArrayFromImage(rawdata)[70:]
    print(data.shape)   
    data = preprocess_normalization(data, 0, 255).astype(np.uint8)
    background = data[0]
    
    label_array = copy.deepcopy(data[0])
    label_array[label_array<100] = 0
    # path_label = 'E:\\Data\\2022-1-7\\IMR-SJTU_ZSJ_20220107_104710_497000\\erode_vessel_simple.nii.gz'
    # label = sitk.ReadImage(path_label)
    # label_array = sitk.GetArrayFromImage(label)

    start_point_x = 170
    start_point_y = 124                  

    # --------------------------------Track by moving window v1
    # step = 1
    # pertential_locates = [(start_point_x, start_point_y-step),(start_point_x-step, start_point_y-step),(start_point_x-step, start_point_y),(start_point_x-step, start_point_y+step),
    #                         (start_point_x, start_point_y+step),(start_point_x+step, start_point_y+step),(start_point_x+step, start_point_y),(start_point_x+step, start_point_y-step)]
    # for i in range(data.shape[0]):
    #     x, y, img = detect_probe(data[i], start_point_x, start_point_y)
    #     start_point_x = x
    #     start_point_y = y
    #     print("The tracked point is: (%d, %d)"%(x,y))
    #     img[x-3:x+3, y-3:y+3] = 9999
    #     cv2.imshow("frame", img)
    #     cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # --------------------------------Track by moving window v2

    tracker_size = 3
    
    for i in range(data.shape[0]):
        img = data[i]
        if i ==0:
            tracker_window = img[start_point_x-tracker_size:start_point_x+tracker_size,start_point_y-tracker_size:start_point_y+tracker_size]
            mean = np.mean(tracker_window)                
        else:
            start_point_x, start_point_y, mean = detect_probe_v3(data[i], start_point_x, start_point_y, mean)
            print("The tracked point is: (%d, %d)"%(start_point_x,start_point_y))
            img[start_point_x-3:start_point_x+3, start_point_y-3:start_point_y+3] = 9999
        cv2.imshow("frame", img)
        # time.sleep(0.1)
        cv2.waitKey(0)                 
    cv2.destroyAllWindows()

    # --------------------------------Track by CamShift
    # track_by_camshift(data, label_array)

    # --------------------------------Track by KCFtracker
    # tracker = kcftracker.KCFTracker(True, True, True)
    # tracker.init([150, 137, 6, 6], background)
    # for i in range(1, data.shape[0]):
    #     boundingbox = tracker.update(data[i])
    #     boundingbox = list(map(int, boundingbox))
    #     print(boundingbox[0], boundingbox[1], boundingbox[2], boundingbox[3])
    #     cv2.rectangle(data[i], (boundingbox[0], boundingbox[1]),
    #                     (boundingbox[0] + boundingbox[2], boundingbox[1] + boundingbox[3]), 255, 1)
    #     cv2.imshow("frame", data[i])
    #     cv2.waitKey(0)
    # cv2.destroyAllWindows()


    

    
 