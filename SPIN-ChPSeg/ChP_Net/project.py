import os
import numpy as np
import nibabel as nib

def get_patch(input,patch_list):
    out_list = []
    for per_list in patch_list:
        out_list.append(input[:,per_list[0]:per_list[1],per_list[2]:per_list[3],per_list[4]:per_list[5]])

    return out_list

def reverse_patch(input,patch_list,shape):
    
    Image = np.zeros(shape=shape)
    for idex,per_list in enumerate(patch_list):
        Image[:,per_list[0]:per_list[1],per_list[2]:per_list[3],per_list[4]:per_list[5]] = input[idex]
    return Image
#

def image2subspace(image = None,proj_matrix = None,rank = 10):
    if len(image.shape) == 3:
        batch , h , w  = image.shape
        vector_length = h * w
    elif len(image.shape) == 4:
        batch , h , w , d = image.shape
        vector_length = h * w * d
    data = image.reshape(batch,vector_length)
    
    proj_data = np.matmul(np.matmul(data,proj_matrix[:rank,:].T),proj_matrix[:rank,:] )

    if len(image.shape) == 3:
        proj_image = proj_data.reshape(batch , h , w)
    elif len(image.shape) == 4:
        proj_image = proj_data.reshape(batch , h , w , d)

    return proj_image


def nii2subspace(image = None,out = None,proj_matrix_L = None, proj_matrix_R = None,patch_list = None,rank = 20):
    if os.path.exists(out):
        return
    image = nib.load(image)
    data,affine,header = image.get_fdata(),image.affine,image.header
    data = data[np.newaxis, ...]
    shape = data.shape
    data_L,data_R = get_patch(data,patch_list)
    data_L_est = image2subspace(image = data_L,proj_matrix = proj_matrix_L,rank = rank)
    data_R_est = image2subspace(image = data_R,proj_matrix = proj_matrix_R,rank = rank)
    data = reverse_patch([data_L_est,data_R_est],patch_list,shape)
    nib.save(nib.Nifti1Image(data[0], affine, header), out)