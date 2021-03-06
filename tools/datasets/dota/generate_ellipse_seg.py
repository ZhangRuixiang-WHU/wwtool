import os
import cv2
import mmcv
import numpy as np

if __name__ == '__main__':
    release_version = 'v1'
    imageset = 'trainval'
    rate = '1.0'
    pointobb_sort_method = 'best'
    extra_info = 'keypoint'

    encode = 'ellipse_seg'   # centernessmask, gaussmask, ellipsemask

    pseudomask_path = './data/dota/{}/{}/{}'.format(release_version, imageset, encode)
    seg_path = './data/dota/{}/{}/obb_seg'.format(release_version, imageset)

    save_path = './data/dota/{}/{}/ellipse_seg'.format(release_version, imageset)
    mmcv.mkdir_or_exist(save_path)

    image_names = os.listdir(pseudomask_path)
    progress_bar = mmcv.ProgressBar(len(image_names))
    for image_name in image_names:
        pseudomask_file = os.path.join(pseudomask_path, image_name)
        seg_file = os.path.join(seg_path, image_name)

        # print(pseudomask_file, seg_file)

        pseudomask = cv2.imread(pseudomask_file)
        seg = cv2.imread(seg_file)
        seg = pseudomask / 255.0 * seg

        save_file = os.path.join(save_path, image_name)
        cv2.imwrite(save_file, seg.astype(np.uint8))
        progress_bar.update()