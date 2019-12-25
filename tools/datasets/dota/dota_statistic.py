import wwtool

coco_dota_class = {1: 'harbor', 
                       2: 'ship', 
                       3: 'small-vehicle', 
                       4: 'large-vehicle', 
                       5: 'storage-tank', 
                       6: 'plane', 
                       7: 'soccer-ball-field', 
                       8: 'bridge', 
                       9: 'baseball-diamond', 
                      10: 'tennis-court', 
                      11: 'helicopter', 
                      12: 'roundabout', 
                      13: 'swimming-pool', 
                      14: 'ground-track-field', 
                      15: 'basketball-court', 
                      16: 'container-crane'}

ann_file_name = ['dota-v1.5', 'trainval', 'v1', '1.0', 'best']
ann_file_name.append('small_object')
ann_file = './data/{}/v1/coco/annotations/{}.json'.format(ann_file_name[0], '_'.join(ann_file_name))

size_measure_by_ratio = False
if size_measure_by_ratio == False:
    size_set = [4*4, 8*8, 16*16, 32*32, 64*64, 128*128, 256*256]
    label_set = ["4*4", "8*8", "16*16", "32*32", "64*64", "128*128", "256*256"]
else:
    size_set = [0.12/100, 1.08/100, 9.72/100]
    label_set = ["0.12/100", "1.08/100", "9.72/100"]

dior_statistic = wwtool.COCO_Statistic(ann_file, size_set=size_set, label_set=label_set, size_measure_by_ratio=size_measure_by_ratio)

# for pie_flag in [False, True]:
#     dior_statistic.total_size_distribution(plot_pie=pie_flag, save_file_name=ann_file_name[:])

dior_statistic.class_size_distribution(coco_class=coco_dota_class, save_file_name=ann_file_name[:])