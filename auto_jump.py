import cv2
import numpy as np
import os
import sys
import time
from matplotlib import pyplot as plt
from IPython import display


screen_x_eff, screen_y_eff = 1125,1958
jumper_foot_offset = 20
holdDt = 1.392
tap_x, tap_y = 600,1000


#load jumper template
jumper_template = cv2.imread('jumper.png')
template_h,template_w = jumper_template.shape[0:2]


def jump(distance):
    dt = int(holdDt * distance)
    rand_tapxy = np.random.randn(4,)*3 #ad some randomness in the tap location
    cmd_msg = 'adb shell input swipe {x1} {y1} {x2} {y2} {dt}'.format(
        x1=tap_x+int(rand_tapxy[0]),y1=tap_y+int(rand_tapxy[1]),
        x2=tap_x+int(rand_tapxy[2]),y2=tap_y+int(rand_tapxy[3]),
        dt=dt)
    os.system(cmd_msg)
    return dt    


def find_position(im_name):
    
    img = cv2.imread(im_name);
    res = cv2.matchTemplate(img,jumper_template,cv2.TM_SQDIFF_NORMED) #find jumper template matching
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print(min_val)
    if min_val>0.3: #fail to find a match
        return -1,-1,img
    
    top_left = min_loc
    bottom_right = (top_left[0] + template_w, top_left[1] + template_h)

    jumper_xy = (top_left[0]+int(template_w*0.5), top_left[1]+template_h-jumper_foot_offset) #jumper base location
    target_xy = (screen_x_eff-jumper_xy[0],screen_y_eff-jumper_xy[1])  #mirror the jumper base location to get the target base location
    
    distance = np.sqrt(np.square(target_xy[0]-jumper_xy[0])+np.square(target_xy[1]-jumper_xy[1])) #compute jump distance

    #print(target_xy,distance)
    cv2.rectangle(img,top_left, bottom_right, 255, 2)   # highlight where the jumper template is found
    cv2.circle(img,jumper_xy, 10, 255, 2)               # highlight jumper base location
    cv2.circle(img,target_xy, 10, 255, 2)               # highlight target base location

    #print(jumper_xy,target_xy,distance)
    return target_xy,distance,img



while True:
    os.system('adb shell screencap /sdcard/1.png');     #take a screenshot
    os.system('adb pull /sdcard/1.png ./scrshot.png');  #download the screenshot to local disk
    
    target_xy,distance,img = find_position('scrshot.png');
    
    plt.clf()
    fig=plt.figure(figsize=(18, 16))
    plt.subplot(111)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.xticks([]), plt.yticks([])
    plt.show()

    display.display(plt.gcf())
    display.clear_output(wait=True)   
    
    if distance<0: #fail to find match
        print('failed');
        break;
    jump(distance);
    time.sleep(2);
    




