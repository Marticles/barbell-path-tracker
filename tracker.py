# -*- coding: utf-8 -*-
import cv2
import dlib
import os
import numpy as np

from collections import deque

class pathTracker(object):
    def __init__(self, windowName = 'default window', videoName = "default video"):

        #自定义追踪属性
        self.selection = None                           #框选追踪目标状态
        self.track_window = None                        #追踪窗口状态   
        self.drag_start = None                          #鼠标拖动状态
        self.speed = 50                                 #视频播放速度
        self.video_size = (960,540)                     #视频大小
        self.box_color = (255,255,255)                  #跟踪器外框颜色
        self.path_color = (0,0,255)                     #路径颜色
    

        #选择追踪器类型
        #                          0        1     2      3         4           5            6              7              8       
        self.tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'Dlib_Tracker', 'CamShift','Template_Matching']
        self.tracker_type = self.tracker_types[6] 

        #创建视频窗口
        cv2.namedWindow(windowName,cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(windowName,self.onmouse)
        self.windowName = windowName

        #打开视频
        self.cap = cv2.VideoCapture(videoName)
        if not self.cap.isOpened():
            print("Video doesn't exit!", videoName)

        #定义一些视频的相关属性
        self.frames_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) #视频总帧数
        self.points = deque(maxlen = self.frames_count) #存放每一帧中追踪目标的中心点

        #判定所选追踪器类型并初始化追踪器
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


    #处理鼠标点击函数
    def onmouse(self,event, x, y, flags, param):

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

    #实时绘制追踪器轮廓,中心点与轨迹函数          
    def drawing(self,image,x,y,w,h,timer):

        center_point_x = int(x+ 0.5*w)
        center_point_y = int(y + 0.5*h)
        center = (center_point_x,center_point_y)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        self.points.appendleft(center)
        cv2.rectangle(image, (int(x),int(y)), (int(x+w),int(y+h)), self.box_color, 2) #画出追踪目标矩形
        cv2.circle(image, center, 2, self.path_color, -1) #中心点
        cv2.putText(image,"(X=" + str(center_point_x) + ",Y=" + str(center_point_y) + ")", (int(x),int(y)),cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.path_color, 2)     
        cv2.putText(image,"FPS=" + str(int(fps)), (40,20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, self.path_color, 2)
        
        for i in range(1, len(self.points)):

            if self.points[i-1] is None or self.points[i] is None:
                continue
            cv2.line(image, self.points[i-1], self.points[i], self.path_color,2) #绘制中心点轨迹


    #目标追踪函数
    def start_tracking(self):
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

            if i == 0: #只有在第一帧时才需要框选目标
                while(True):
                    img_first = image.copy()
                    if self.track_window:
                        cv2.rectangle(img_first, (self.track_window[0],self.track_window[1]), (self.track_window[2], self.track_window[3]), self.box_color, 1)
                    elif self.selection:
                        cv2.rectangle(img_first, (self.selection[0],self.selection[1]), (self.selection[2], self.selection[3]), self.box_color, 1)
                    cv2.imshow(self.windowName, img_first)

                    if cv2.waitKey(self.speed) == 13: #Enter开始追踪
                        break

                if self.tracker_type == 'Dlib_Tracker':

                        self.tracker.start_track(image, dlib.rectangle(self.track_window[0], self.track_window[1], self.track_window[2], self.track_window[3]))
            
                elif self.tracker_type == 'CamShift':

                    tracker_box = (self.track_window[0], self.track_window[1], self.track_window[2]-self.track_window[0] , self.track_window[3]-self.track_window[1])
                    roi = image[self.track_window[1]:self.track_window[3],self.track_window[0]:self.track_window[2]]
                    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
                    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
                    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
                    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )

                elif self.tracker_type == 'Template_Matching':

                    '''
                        1.平方差匹配 method = CV_TM_SQDIFF
                        2.标准平方差匹配 method = CV_TM_SQDIFF_NORMED
                        3.相关匹配 method = CV_TM_CCORR
                        4.标准相关匹配 method = CV_TM_CCORR_NORMED
                        5.相关匹配 method = CV_TM_CCOEFF
                        6.标准相关匹配 method = CV_TM_CCOEFF_NORMED

                        cv2.matchTemplate()方法严格要求模板与背景为同一数据类型(CV_8U or CV_32F)

                    '''
                    method = cv2.TM_CCOEFF_NORMED
                    template = image[self.track_window[1]:self.track_window[3],self.track_window[0]:self.track_window[2]]
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) 
                    template = template.astype(np.float32)
            
                else : #OpenCV预置的五种追踪器
                    ret = self.tracker.init(image, (self.track_window[0], self.track_window[1], self.track_window[2]-self.track_window[0] , self.track_window[3]-self.track_window[1]))

            #框选完目标后，第一帧结束就开始追踪目标
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

                #平方差匹配CV_TM_SQDIFF与标准平方差匹配TM_SQDIFF_NORMED最佳匹配为最小值 0，匹配值越大匹配越差，其余则相反
                
                if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                    x = min_loc[0]
                    y = min_loc[1]
                else:
                    x = max_loc[0]
                    y = max_loc[1]

        
            else: #OpenCV预置的五种追踪器
              
                ret,tracker_box = self.tracker.update(image)
                x,y,w,h = tracker_box
            
            self.drawing(image,x,y,w,h,timer)
            cv2.imshow(self.windowName,image)

            if cv2.waitKey(self.speed) == 27: #Esc结束
                break

            i += 1

            if i == self.frames_count:
                cv2.imwrite('Video/track_result.jpg',image)

        cv2.destroyAllWindows()

if __name__ == '__main__':
    myTracker = pathTracker(windowName = 'myTracker',videoName = "Video/LuXiaojun.mp4")
    myTracker.start_tracking()