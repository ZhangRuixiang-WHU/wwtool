import os
import json
import csv
import numpy as np
import wwtool
from tqdm import tqdm
import pandas as pd
from collections import defaultdict
import xml.etree.ElementTree as ET
from pycocotools import mask


def voc_parse(label_file):
    """parse VOC style dataset label file
    
    Arguments:
        label_file {str} -- label file path
    
    Returns:
        dict, {'bbox': [xmin, ymin, xmax, ymax], 'label': class_name} -- objects' location and class
    """
    tree = ET.parse(label_file)
    root = tree.getroot()
    objects = []
    for single_object in root.findall('object'):
        bndbox = single_object.find('bndbox')
        object_struct = {}

        xmin = float(bndbox.find('xmin').text)
        ymin = float(bndbox.find('ymin').text)
        xmax = float(bndbox.find('xmax').text)
        ymax = float(bndbox.find('ymax').text)

        object_struct['bbox'] = [xmin, ymin, xmax, ymax]
        object_struct['label'] = single_object.find('name').text
        
        objects.append(object_struct)
    return objects


def rovoc_parse(label_file):
    """parse rotation VOC style dataset label file
    
    Arguments:
        label_file {str} -- label file path
    
    Returns:
        dict, {'bbox': [cx, cy, w, h, theta (rad/s)], 'label': class_name} -- objects' location and class
    """
    tree = ET.parse(label_file)
    root = tree.getroot()
    objects = []
    for single_object in root.findall('object'):
        robndbox = single_object.find('robndbox')
        object_struct = {}

        cx = float(robndbox.find('cx').text)
        cy = float(robndbox.find('cy').text)
        w = float(robndbox.find('w').text)
        h = float(robndbox.find('h').text)
        theta = float(robndbox.find('angle').text)

        object_struct['bbox'] = [cx, cy, w, h, theta]
        object_struct['label'] = single_object.find('name').text
        
        objects.append(object_struct)
    return objects

def simpletxt_parse(label_file):
    """parse simpletxt style dataset label file
    
    Arguments:
        label_file {str} -- label file path
    
    Returns:
        dict, {'bbox': [...], 'label': class_name} -- objects' location and class
    """
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    objects = []
    basic_label_str = " "
    for line in lines:
        object_struct = dict()
        line = line.rstrip().split(' ')
        label = basic_label_str.join(line[4:])
        bbox = [float(_) for _ in line[0:4]]
        object_struct['bbox'] = bbox
        object_struct['label'] = label
        objects.append(object_struct)
    
    return objects

def dota_parse(label_file):
    """parse dota style dataset label file
    
    Arguments:
        label_file {str} -- label file path
    
    Returns:
        dict, {'bbox': [...], 'label': class_name} -- objects' location and class
    """
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    objects = []
    for line in lines:
        object_struct = dict()
        line = line.rstrip().split(' ')
        label = line[8]
        pointobb = [float(xy) for xy in line[:8]]
        bbox = wwtool.pointobb2bbox(pointobb)
        object_struct['bbox'] = bbox
        object_struct['label'] = label
        object_struct['pointobb'] = pointobb
        objects.append(object_struct)
    
    return objects

class XVIEW_PARSE():
    def __init__(self, json_file, xview_class_labels_file):
        with open(json_file) as f:
            data = json.load(f)

        self.coords = np.zeros((len(data['features']), 4))
        self.image_names = np.zeros((len(data['features'])), dtype="object")
        self.classes = np.zeros((len(data['features'])))

        for i in tqdm(range(len(data['features']))):
            if data['features'][i]['properties']['bounds_imcoords'] != []:
                b_id = data['features'][i]['properties']['image_id']
                val = np.array([int(num) for num in data['features'][i]['properties']['bounds_imcoords'].split(",")])
                self.image_names[i] = b_id
                self.classes[i] = data['features'][i]['properties']['type_id']
                if val.shape[0] != 4:
                    print("Issues at %d!" % i)
                else:
                    self.coords[i] = val
            else:
                self.image_names[i] = 'None'

        self.labels = {}
        with open(xview_class_labels_file) as f:
            for row in csv.reader(f):
                self.labels[int(row[0].split(":")[0])] = row[0].split(":")[1]

        print("Finish to load xView json file!")
    
    def xview_parse(self, image_name):
        """bbox -> [xmin, ymin, xmax, ymax]
        
        Arguments:
            image_name {str} -- image file name
        
        Returns:
            objects {bboxes, labels} -- object dict
        """
        bboxes = self.coords[self.image_names == image_name]
        labels = self.classes[self.image_names == image_name].astype(np.int64)

        objects = []
        for bbox, label in zip(bboxes, labels):
            object_struct = dict()
            object_struct['bbox'] = bbox
            object_struct['label'] = self.labels[label]
            objects.append(object_struct)
        
        return objects

def visdrone_parse(label_file):
    """parse visdrone style dataset label file
    
    Arguments:
        label_file {str} -- label file path 
        (<bbox_left>, <bbox_top>, <bbox_width>, <bbox_height>, <score>, <object_category>, <truncation>, <occlusion>)
    
    Returns:
        dict, {'bbox': [xmin, ymin, xmax, ymax], 'label': class_name} -- objects' location and class
    """
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    objects = []
    for line in lines:
        object_struct = dict()
        line = line.rstrip().split(',')
        label = line[5]
        bbox = [float(_) for _ in line[0:4]]
        object_struct['bbox'] = wwtool.xywh2xyxy(bbox)
        object_struct['label'] = label
        if object_struct['label'] == '0' or object_struct['label'] == '11':
            continue
        objects.append(object_struct)
    
    return objects

class UAVDT_PARSE():
    """
    <frame_index>,<target_id>,<bbox_left>,<bbox_top>,<bbox_width>,<bbox_height>,<out-of-view>,<occlusion>,<object_category>
    """
    def __init__(self, label_fold):
        self.uavdt_objects = dict()
        for label_file in os.listdir(label_fold):
            seq_name = label_file.split('_')[0]
            with open(os.path.join(label_fold, label_file), 'r') as f:
                lines = f.readlines()

            single_seq_objects = dict()
            for line in lines:
                image_idx, object_id, xmin, ymin, w, h, oov, occlusion, category = [int(_) for _ in line.rstrip().split(',')]
                xmax = xmin + w
                ymax = ymin + h
                if "img{:0>6d}".format(image_idx) not in single_seq_objects:
                    single_seq_objects["img{:0>6d}".format(image_idx)] = []
                else:
                    single_seq_objects["img{:0>6d}".format(image_idx)].append([xmin, ymin, xmax, ymax, category])
            self.uavdt_objects[seq_name] = single_seq_objects

        print("Finish to load UAVDT txt file!")
    
    def uavdt_parse(self, seq_name, image_name):
        try:
            seq_objects = self.uavdt_objects[seq_name]
            image_index_objects = seq_objects[image_name]
        except KeyError:
            print("Skip this image.")
            return []

        objects = []
        for image_index_object in image_index_objects:
            object_struct = dict()
            object_struct['bbox'] = image_index_object[0:4]
            object_struct['label'] = str(image_index_object[4])
            objects.append(object_struct)
        
        return objects

class StanfordCompusParse():
    """
    <target_id>, <xmin>, <ymin>, <xmax>, <ymax>, <frame_id>, <lost>, <occluded>, <generated>, <label>
    """
    def __init__(self, label_fold):
        self.scenes = ('bookstore', 'coupa', 'deathCircle', 'gates', 'hyang', 'little', 'nexus', 'quad')
        self.stanford_compus_objects = dict()
        
        for scene_name in self.scenes:
            for video_name in os.listdir(os.path.join(label_fold, scene_name)):
                label_file = os.path.join(label_fold, scene_name, video_name, 'annotations.txt')

                with open(label_file, 'r') as f:
                    lines = f.readlines()

                for line in lines:
                    target_id, xmin, ymin, xmax, ymax, frame_id, lost, occluded, generated = [int(_) for _ in line.rstrip().split(' ')[0:-1]]
                    label = line.rstrip().split(' ')[-1].split('"')[1]

                    if lost == 1 or occluded == 1:
                        continue
                    
                    if (scene_name, video_name, frame_id) not in self.stanford_compus_objects:
                        self.stanford_compus_objects[(scene_name, video_name, frame_id)] = []
                    else:
                        self.stanford_compus_objects[(scene_name, video_name, frame_id)].append([xmin, ymin, xmax, ymax, label])
        
        print("Finish to load Stanford Compus txt file!")
    
    def stanford_compus_parse(self, scene_name, video_name, frame_id):
        # print(self.stanford_compus_objects.keys())
        try:
            frame_index_objects = self.stanford_compus_objects[(scene_name, video_name, frame_id)]
        except KeyError:
            print("Skip this image.")
            return []

        objects = []
        for frame_index_object in frame_index_objects:
            object_struct = dict()
            object_struct['bbox'] = frame_index_object[0:4]
            object_struct['label'] = str(frame_index_object[4])
            objects.append(object_struct)
        
        return objects

class AirbusShipParse():
    """
    <target_id>, <xmin>, <ymin>, <xmax>, <ymax>, <frame_id>, <lost>, <occluded>, <generated>, <label>
    """
    def __init__(self, label_file):
        self.airbus_ship_objects = defaultdict(list)

        self.anno_data = pd.read_csv(label_file)
        self.anno_data = self.anno_data.dropna(axis=0)

        for idx in range(self.anno_data.shape[0]):
            image_name = self.anno_data.iloc[idx, 0]
            image_objects = self.anno_data.iloc[idx, 1]

            binary_mask = self.rle_decode(image_objects)
            binary_mask_encoded = mask.encode(np.asfortranarray(binary_mask.astype(np.uint8)))
            bounding_box = mask.toBbox(binary_mask_encoded)
            xmin, ymin, xmax, ymax = wwtool.xywh2xyxy(bounding_box)

            self.airbus_ship_objects[image_name].append([xmin, ymin, xmax, ymax])

    def rle_decode(self, mask_rle, shape=(768, 768)):
        s = mask_rle.split()
        starts =  np.asarray(s[0::2], dtype=int)
        lengths = np.asarray(s[1::2], dtype=int)

        starts -= 1
        ends = starts + lengths
        img = np.zeros(shape[0]*shape[1], dtype=np.uint8)
        for lo, hi in zip(starts, ends):
            img[lo:hi] = 1
        return img.reshape(shape).T

    def airbus_ship_parse(self, image_name):
        try:
            image_objects = self.airbus_ship_objects[image_name]
        except KeyError:
            print("Skip this image.")
            return []

        objects = []
        for image_object in image_objects:
            object_struct = dict()
            object_struct['bbox'] = image_object[0:4]
            object_struct['label'] = "1"
            objects.append(object_struct)
        
        return objects