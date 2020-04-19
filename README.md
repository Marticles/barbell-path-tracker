# Barbell-Path-Tracker
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)
![](https://img.shields.io/badge/language-python-orange.svg)

![](Result/luxiaojun.gif)    

![](Result/luxiaojun.jpg)

>*Take my favourite weightlifter Lu XiaoJun as an example*     
## Description  
        
There are 9 different trackers you can choose to track barbell's path, including BOOSTING, MIL, KCF, TLD, MEDIANFLOW,， GOTURN, Dlib_Tracker, CamShift and TemplateMatching. This tracker is not only used to track barbell, you can also use it to track other objects, like cars or some moving objects.
    
关于这个简单的追踪器的中文说明在这里：[(｡･ω･｡) 点我点我](http://marticles.github.io/2018/05/05/基于OpenCV与Dlib的杠铃轨迹追踪器/)

## Start Tracking

Firstly you need to create a bounding box around the bar as the target. By clicking the left mouse button you can customize  this bounding box. Once you have set up the target, then press <kbd>Enter</kbd> to start tracking. 

Use <kbd>Esc</kbd> to stop tracking. 

I hope this small program can help you to lift more weights. 

"Yeah buddy! Light weight baby!" 🏋

## Comparison
The comparison results are as follows.

<img src="Result/avg_fps.svg">      
      
<img src="Result/fps.svg">      
      

## Requirements   
     
* OpenCV3
* Dlib
* Numpy
    
 



