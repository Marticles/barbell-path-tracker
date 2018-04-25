# BarPath_Tracking
![Image](https://pic4.zhimg.com/v2-f991d9567a65c74ada7cf19c8f2d43b0_b.gif)    

![Image](https://pic4.zhimg.com/v2-221a1c9d7f34c2fbeb045041760b9804_b.jpg)        
>*Take my favourite weightlifter Lu XiaoJun as an example*     
## Description  
        
There are 9 different trackers you can choose to track the barbell path,including BOOSTING,MIL,KCF,TLD, MEDIANFLOW, GOTURN, Dlib_Tracker, CamShift and Template_Matching.Not only the barbell path,you can also use these trackers to track other object,like a car or anything else.Some of the comparison results are as follows.    

<img src="Result/avg_fps.svg">      
      
<img src="Result/fps.svg">      
      

## Requirements   
     
* OpenCV3
* Dlib
* Numpy
    
## Start Tracking    
Firstly You need to create a bounding box around the bar(or the obeject) to be tracked.Click the left mouse button to select the bounding box.Then press <kbd>Enter</kbd> to start the tracking.If you want to close the video,just press <kbd>Esc</kbd>.I hope this simple program can help you to lift more weight.    



