#coding:utf-8
"""
@auther tozawa
"""
import sys, os, copy, time, yaml
import numpy as np
import SimpleITK as sitk

def read_mhd_and_raw(path, numpyFlag=True):
    """
    This function use sitk
    path : Meta data path
    ex. /hogehoge.mhd
    numpyFlag : Return numpyArray or sitkArray
    return : numpyArray(numpyFlag=True)
    Note ex.3D :numpyArray axis=[z,y,x], sitkArray axis=(z,y,x)
    """
    img = sitk.ReadImage(path)
    if not numpyFlag:
        return img

    nda = sitk.GetArrayFromImage(img) #(img(x,y,z)->numpyArray(z,y,x))
    return nda

def write_mhd_and_raw(Data, path, space=[], origin=[]):
    """
    This function use sitk
    Data : sitkArray
    path : Meta data path
    ex. /hogehoge.mhd
    """
    if isinstance(Data, np.ndarray):
        Data = sitk.GetImageFromArray(Data)
    if not isinstance(Data, sitk.SimpleITK.Image):
        print('Please check your ''Data'' class')
        return False
    ndims = Data.GetDimension()
    _space = [1. if len(space) != ndims else space[i] for i in range(ndims)]
    _origin = [0. if len(origin) != ndims else origin[i] for i in range(ndims)]

    Data.SetSpacing(_space)
    Data.SetOrigin(_origin)
    data_dir, file_name = os.path.split(path)
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)

    sitk.WriteImage(Data, path)

    return True

def save_args(output_dir, args):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open('{}/config_{}.yml'.format(output_dir, time.strftime('%Y-%m-%d_%H-%M-%S')), 'w') as f:
        f.write(yaml.dump(vars(args), default_flow_style=False))
