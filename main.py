# coding: utf-8

import os, sys, time
import numpy as np
import pandas as pd
import SimpleITK as sitk
import argparse, glob
import sklearn.metrics.pairwise
import utils.ioFunctions as IO

def distance_sklearn_metrics(z, k=4, metric='euclidean'):
    """Compute exact pairwise distances."""
    # Adapted from https://github.com/mdeff/cnn_graph/blob/master/lib/graph.py
    d = sklearn.metrics.pairwise.pairwise_distances(
        z, metric=metric, n_jobs=-2)
    # k-NN graph.
    idx = np.argsort(d)[:, 1:k + 1]
    d.sort()
    d = d[:, 1:k + 1]
    return d, idx

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputImageFile', '-i', help='input image file')
    parser.add_argument('--inputCsvFileDir', '-icfd', help='Directory path to input csv files')
    parser.add_argument('--outputImageFile', '-o', help='output image file')

    parser.add_argument('--csvFileName', type=str, default='3d_bbox_z=')
    parser.add_argument('--ax_threshold', type=float, default=12.0,
                            help='Range of permission as cell at axial')
    # parser.add_argument('--coro_threshold', type=float, default=3.0,
    #                         help='Range of permission as cell at coronal')

    args = parser.parse_args()

    print('----- Save args -----')
    base_dir = os.path.dirname(os.path.abspath( __file__ ))
    output_dir = os.path.dirname(args.outputImageFile)
    IO.save_args(output_dir, args)

    print('----- Read image -----')
    sitkImg = IO.read_mhd_and_raw(args.inputImageFile, numpyFlag=False)
    img = sitk.GetArrayFromImage(sitkImg)

    print('----- Lets unification -----')
    print('*******************')
    print('----- Expect that contain large number more than 10000 to csv file if bbox detector cant find cell at each slice. -----')
    print('----- This means no empty file, if you have empty file, please input over 10000 to empty file')
    print('*******************')

    fnames = glob.glob('{}/*.csv'.format(args.inputCsvFileDir))
    bbox_list = []
    total_bbox_df = pd.DataFrame()
    print('---- Read all bbox data ----')
    for z in range(len(fnames)):
        filename = '{}{}.csv'.format(args.csvFileName, z)
        bbox_df = pd.read_csv('{}/{}'.format(args.inputCsvFileDir, filename), names=("xmin","ymin","xmax","ymax"))
        # Calc bounding box center
        bbox_df['z'] = z
        bbox_df['x_center'] = (bbox_df['xmax'] - bbox_df['xmin']) /2 + bbox_df['xmin']
        bbox_df['y_center'] = (bbox_df['ymax'] - bbox_df['ymin']) /2 + bbox_df['ymin']
        total_bbox_df = total_bbox_df.append(bbox_df, ignore_index = True)

    print('))))))) Removeeeeeeeeeeeeeee 10000 )))))))')
    total_bbox_df = total_bbox_df[~(total_bbox_df['xmin']>=10000)].reset_index(drop=True)
    print('Total 2D bbox: {}'.format(len(total_bbox_df)))
    total_bbox_df['pre_bbox_id'] = 100000
    total_bbox_df['attach_flag'] = False

    print('==== Attach pre bbox id ====')
    ax_plane = total_bbox_df[['x_center', 'y_center']].values
    distances, idxes = distance_sklearn_metrics(ax_plane, k=len(ax_plane))
    id = 0
    for row, (dist, idx)  in enumerate(zip(distances, idxes)):
        print('Now row: {}'.format(row))
        # Same id index
        idx = idx[dist<args.ax_threshold]

        # Attach interest of row
        if total_bbox_df.at[row, 'attach_flag']:
            #print('   this row is already attached')
            continue
        total_bbox_df.at[row, 'attach_flag'] = True
        total_bbox_df.at[row, 'pre_bbox_id'] = id

        for i in idx:
            if  total_bbox_df.at[i, 'attach_flag']:
                continue
            total_bbox_df.at[i, 'attach_flag'] = True
            total_bbox_df.at[i, 'pre_bbox_id'] = id
        id += 1

    print('#####＼(^o^)／ Attach True bbox configs ＼(^o^)／#####')
    output_bbox_df = pd.DataFrame()
    for pre_id in range(len(total_bbox_df['pre_bbox_id'].unique())):
        temp_df = total_bbox_df[total_bbox_df['pre_bbox_id']==pre_id]
        xmin, xmax = temp_df['xmin'].min(), temp_df['xmax'].max()
        ymin, ymax = temp_df['ymin'].min(), temp_df['ymax'].max()
        zmin, zmax = temp_df['z'].min(), temp_df['z'].max()
        result_df = pd.DataFrame({'bbox_id':[pre_id],
                                    'xmin':[xmin], 'xmax':[xmax],
                                    'ymin':[ymin], 'ymax':[ymax],
                                    'zmin':[zmin], 'zmax':[zmax]})
        output_bbox_df = output_bbox_df.append(result_df, ignore_index = True)

    output_bbox_df.to_csv('{}/bbox_results.csv'.format(output_dir), index=False, encoding='utf-8', mode='w')
    print('%%%%%% Draw label %%%%%%')
    out = np.zeros(img.shape, dtype=np.uint8)
    for index, row in output_bbox_df.iterrows():
        xmin, xmax = int(row['xmin']), int(row['xmax'])
        ymin, ymax = int(row['ymin']), int(row['ymax'])
        zmin, zmax = int(row['zmin']), int(row['zmax'])
        out[zmin:zmax, ymin:ymax, xmin:xmax ] = row['bbox_id']

    IO.write_mhd_and_raw(out, args.outputImageFile, space=[1.75, 1.75, 5.0])
    print('%%%%%% Done dadan %%%%%%')



if __name__ == '__main__':
    main()
