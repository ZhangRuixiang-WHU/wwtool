## WWTOOL
wwtool is a Python library for Computer Vision Research.

It will provide the following functionalities.

- Basic parse and dump functions for object detection datasets
- Detection annotation visualization
- Dataset convert
- Toolkit for object detection dataset
    - [DOTA](https://captain-whu.github.io/DOTA/index.html)
    - [VisDrone](http://aiskyeye.com/)
    - [UAV-BD](https://jwwangchn.cn/UAV-BD)
    - ...

### Requirements

- Python 3.7
- Pytorch 1.0+
- CUDA 8.0+
- [mmcv](https://github.com/open-mmlab/mmcv)

### Installation
```
git clone https://github.com/jwwangchn/wwtool.git
cd wwtool
python setup.py develop
```

### Future works
- [x] Statistic function for object detetion datasets
- [x] Split large image to sub-images
- [ ] Results generation tools for dota and visdrone dataset
- [ ] Offline data augmentation
- [ ] Online data augmentation

### Structure
- scripts
- tests
- tools
- wwtool
    - cnn:              CNN Modules by PyTorch
    - models:           Models for detection, classification and segmentation
    - ops:              C++ or Cython codes for CNN operation
    - datasets:         Create and read data from dataset
    - transforms:       bbox and image transformation
        - image
        - bbox
    - fileio:           file operation
        - image
        - file
        - label
    - visualization:    code for visualization
        - image
    - utils:            tools for other tasks
        - pid
        - email
        - uart
        - path
        - config
        - progressbar