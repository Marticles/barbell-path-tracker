# -*- coding: utf-8 -*-
# author: marticles
import cv2
import dlib
import os
import numpy as np
from collections import deque

class pathTracker(object):
    def __init__(self, windowName = 'default window', videoName = "default video"):
        self.selection = None
        self.track_window = None
        self.drag_start = None
        self.speed = 50  
        self.video_size = (960,540)     
        self.box_color = (255,255,255)      
        self.path_color = (0,0,255)
        #                          0        1     2      3         4           5            6              7              8       
        self.tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'Dlib_Tracker', 'CamShift','Template_Matching']
        self.tracker_type = self.tracker_types[6] 
        # create tracker window
        cv2.namedWindow(windowName,cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(windowName,self.onmouse)
        self.windowName = windowName
        # load video
        self.cap = cv2.VideoCapture(videoName)
        if not self.cap.isOpened():
            print("Video doesn't exit!", videoName)
        self.frames_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # store all center points for each frame
        self.points = deque(maxlen = self.frames_count)

        # init tracker
        if self.tracker_type == 'BOOSTING':
            self.tracker = cv2.TrackerBoosting_create()
        elif self.tracker_type == 'MIL':
            self.tracker = cv2.TrackerMIL_create() 
        elif self.tracker_type == 'KCF':
            self.tracker = cv2.TrackerKCF_create() 
        elif self.tracker_type == 'TLD':
            self.tracker = cv2.TrackerTLD_create()  
        elif self.tracker_type == 'MEDIANFLOW':
            self.tracker = cv2.TrackerMedianFlow_create()   
        elif self.tracker_type == 'GOTURN':
            self.tracker = cv2.TrackerGOTURN_create()  
        elif self.tracker_type == 'Dlib_Tracker':
            self.tracker = dlib.correlation_tracker()

    def onmouse(self,event, x, y, flags, param):
        """
        On mouse
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            self.track_window = None
        if self.drag_start:
            xmin = min(x, self.drag_start[0])
            ymin = min(y, self.drag_start[1])
            xmax = max(x, self.drag_start[0])
            ymax = max(y, self.drag_start[1])
            self.selection = (xmin, ymin, xmax, ymax)
        if event == cv2.EVENT_LBUTTONUP:
            self.drag_start = None
            self.track_window = self.selection
            self.selection = None
          
    def drawing(self,image,x,y,w,h,timer):
        """
        Drawing the bound, center point and path for tracker in real-time
        """
        center_point_x = int(x+ 0.5*w)
        center_point_y = int(y + 0.5*h)
        center = (center_point_x,center_point_y)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        self.points.appendleft(center)
        # tracker's bound
        cv2.rectangle(image, (int(x),int(y)), (int(x+w),int(y+h)), self.box_color, 2)
        # center point
        cv2.circle(image, center, 2, self.path_color, -1)
        # coordinate
        cv2.putText(image,"(X=" + str(center_point_x) + ",Y=" + str(center_point_y) + ")", (int(x),int(y)),cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.path_color, 2)     
        # fps
        cv2.putText(image,"FPS=" + str(int(fps)), (40,20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, self.path_color, 2)
        for i in range(1, len(self.points)):
            if self.points[i-1] is None or self.points[i] is None:
                continue
            # path of center point
            cv2.line(image, self.points[i-1], self.points[i], self.path_color,2)

    def start_tracking(self):
        """
        tracking!
        """
        i = 0
        for f in range(self.frames_count):
            timer = cv2.getTickCount()
            ret, self.frame = self.cap.read()
            if not ret:
                print("End!")
                break
            print("Processing Frame {}".format(i))
            img_raw = self.frame
            image = cv2.resize(img_raw.copy(), self.video_size, interpolation = cv2.INTER_CUBIC)
            # only need to select object on the first frame
            if i == 0: 
                while(True):
                    img_first = image.copy()
                    if self.track_window:
                        cv2.rectangle(img_first, (self.track_window[0],self.track_window[1]), (self.track_window[2], self.track_window[3]), self.box_color, 1)
                    elif self.selection:
                        cv2.rectangle(img_first, (self.selection[0],self.selection[1]), (self.selection[2], self.selection[3]), self.box_color, 1)
                    cv2.imshow(self.windowName, img_first)
                    # if press enter then selection is end
                    if cv2.waitKey(self.speed) == 13:
                        break
                # Dlib
                if self.tracker_type == 'Dlib_Tracker':
                        self.tracker.start_track(image, dlib.rectangle(self.track_window[0], self.track_window[1], self.track_window[2], self.track_window[3]))
                # CameShift
                elif self.tracker_type == 'CamShift':
                    tracker_box = (self.track_window[0], self.track_window[1], self.track_window[2]-self.track_window[0] , self.track_window[3]-self.track_window[1])
                    roi = image[self.track_window[1]:self.track_window[3],self.track_window[0]:self.track_window[2]]
                    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
                    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
                    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
                    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
                # Template_Matching
                elif self.tracker_type == 'Template_Matching':
                    method = cv2.TM_CCOEFF_NORMED
                    template = image[self.track_window[1]:self.track_window[3],self.track_window[0]:self.track_window[2]]
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) 
                    template = template.astype(np.float32)
                # Others
                else : 
                    ret = self.tracker.init(image, (self.track_window[0], self.track_window[1], self.track_window[2]-self.track_window[0] , self.track_window[3]-self.track_window[1]))

            # start tracking at the end of the first frame
            # (x, y) is the left-top point's postion of tracker's bound
            # w and h is width and height of tracker's bound
            if self.tracker_type == 'Dlib_Tracker':
                self.tracker.update(image)
                tracker_box = self.tracker.get_position()
                x,y,w,h = tracker_box.left(),tracker_box.top(),tracker_box.width(),tracker_box.height()
            
            elif self.tracker_type == 'CamShift':
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)
                ret, tracker_box = cv2.CamShift(dst, tracker_box, term_crit)        
                x,y,w,h = tracker_box

            elif self.tracker_type == 'Template_Matching':
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                gray = gray.astype(np.float32)
                res = cv2.matchTemplate(gray, template, method)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                w,h = template.shape[::-1]
                if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                    x = min_loc[0]
                    y = min_loc[1]
                else:
                    x = max_loc[0]
                    y = max_loc[1]
            else:
                ret,tracker_box = self.tracker.update(image)
                x,y,w,h = tracker_box
            self.drawing(image,x,y,w,h,timer)
            cv2.imshow(self.windowName,image)
            # if press esc
            if cv2.waitKey(self.speed) == 27:
                break
            i += 1
            # save picture
            if i == self.frames_count:
                cv2.imwrite('Video/track_result.jpg',image)
        cv2.destroyAllWindows()

if __name__ == '__main__':
    myTracker = pathTracker(windowName = 'myTracker',videoName = "Video/LuXiaojun.mp4")
    myTracker.start_tracking()
