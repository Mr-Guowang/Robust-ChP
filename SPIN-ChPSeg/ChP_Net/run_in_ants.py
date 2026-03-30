import os
import argparse
import sys
from pathlib import Path
import shutil
from project import nii2subspace
import torch
import nibabel as nib
from analysis import chp_refine,compute_chp_volume_surface
from bayesian import make_uncertainity

FILE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FILE_DIR
os.chdir(PROJECT_ROOT)

parser = argparse.ArgumentParser(description="Param of Chp Segmentation")
parser.add_argument("--input", type=str, default='./T1w_N4.nii.gz', help="The absolute path of T1w image")
parser.add_argument("--output",type=str, default='./demo/New', help="The absolute path of the output folder")
parser.add_argument("--gpu", type=str, default='2', help="The gpu id")
parser.add_argument("--modal", type=str, default='T1w', help="the input modality")
parser.add_argument("--analysis", action="store_true", help="Enable analysis mode")
parser.add_argument("--use_ants", action="store_true", help="Enable analysis mode")
args = parser.parse_args()

print("╔════════════════════════════════════════════════════════════╗")
print("║  Robust-ChP | Robust Choroid Plexus Segmentation Framework ║")
print("║  GitHub: https://github.com/Mr-Guowang/Robust-ChP          ║")
print("╚════════════════════════════════════════════════════════════╝")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
Modal = args.modal
input = args.input
output_path = args.output
if not os.path.exists(input):
    print(f'The input "{input}" does not exist !!!')
    print('━━━━━━━━━━━━━━━━━━━ Please check the input file! ━━━━━━━━━━━━━━━━━━━')
    sys.exit(1)
else:
    print(f'The input is → "{input}"')
    print(f'The modality is → "{Modal}"')
    print('━━━━━━━━━━━━━━━━━━━ Robust ChP starts running ━━━━━━━━━━━━━━━━━━━')
        
if not args.analysis:
    print('######################################################################')
    print('The analysis and subdivision of the choroid plexus have not been conducted.')
    print('If necessary, please add the parameter "--analysis"')

gpu = args.gpu
if gpu == '-1':
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    print('######################################################################')
    print(f'Using CPU for the whole Pipeline')
else:
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu
    print('######################################################################')
    print(f'Using GPU:{gpu} for the whole Pipeline')

save_ChP_Seg = os.path.join(output_path,'step_4_Robust-ChP') 
os.makedirs(save_ChP_Seg,exist_ok=True)

save_preprocess = os.path.join(output_path,'step_1_T1w_process_ANTs-2.4.0')
os.makedirs(save_preprocess,exist_ok=True)

print('######################################################################')
print('1. N4 bias correction')
print('    if ANTs process has been done, please move the files to "output_path/step_1_T1w_process_ANTs-2.4.0"')
N4 = os.path.join(save_preprocess,f'{Modal}_N4.nii.gz')
brain = os.path.join(save_preprocess,f'{Modal}_brain.nii.gz')
brain_mask = os.path.join(save_preprocess,f'{Modal}_mask.nii.gz')
if not os.path.exists(N4):
    os.system(f'N4BiasFieldCorrection -i {input} -o {N4}')


print('######################################################################')
print('2. Skull stripping (synthstrip---fast deep learning based method)')
if not os.path.exists(brain):
    os.system(f'mri_synthstrip -i {N4} -o {brain} -m {brain_mask}')

# register 2 mni space
print('######################################################################')
print('3 & 4 ANTs---Affine & nonlinear to mni space.')
mni_brain = '../checkpoint/atlas/MNI152_T1.nii'
chp_atlas = '../checkpoint/atlas/ChP_atlas.nii.gz'
T1w_registration = os.path.join(save_preprocess,'T1w2MNI')
T1w_affine = os.path.join(save_preprocess,'T1w2MNI_affine.nii.gz')
T1w_registration = os.path.join(save_preprocess,'T1w2MNI')
T1w2mni0GenericAffine=T1w_registration+'0GenericAffine.mat'
T1w2mni1Warp=T1w_registration+'1Warp.nii.gz'
T1w2mni1InverseWarp = T1w_registration+'1InverseWarp.nii.gz'
T1w_affine = os.path.join(save_preprocess,'T1w2MNI_affine.nii.gz')
if not os.path.exists(T1w2mni1Warp):
    os.system(f'antsRegistrationSyN.sh -d 3 -f {mni_brain} -m {brain} -o {T1w_registration} -t s -n 64') # 
    os.system(f'antsApplyTransforms -d 3 -i {brain} -r {mni_brain} -o {T1w_affine} -t {T1w2mni0GenericAffine}')

# presegmentation by 3d U-Net
tmp_path = os.path.join(save_preprocess,'preseg')
tmp_out = os.path.join(save_preprocess,'tmp_out')
os.makedirs(tmp_path,exist_ok=True)
os.makedirs(tmp_out,exist_ok=True)
T1w4nn = os.path.join(tmp_path,'T1w_0000.nii.gz')
T1w4nnseg = os.path.join(tmp_out,'T1w.nii.gz')
preseg = os.path.join(tmp_out,'T1w4nn.nii.gz')
shutil.copy(N4, T1w4nn)
print('######################################################################')
print('Presegmentation by 3d U-Net, emplement by nnunet framework')
if not os.path.exists(preseg):
    if gpu == '-1':
        os.system(f'OMP_NUM_THREADS=1 /opt/conda/envs/nn/bin/nnUNetv2_predict -i {tmp_path} -o {tmp_out} -d 2 -f 0 -c 3d_fullres -device cpu')
    else:
        os.system(f'OMP_NUM_THREADS=1 CUDA_VISIBLE_DEVICES={gpu} /opt/conda/envs/nn/bin/nnUNetv2_predict -i {tmp_path} -o {tmp_out} -d 2 -f 0 -c 3d_fullres')
    os.system(f'antsApplyTransforms -d 3 -i {T1w4nnseg} -r {brain} -o {preseg} -t [{T1w2mni0GenericAffine}, 1 ] -n NearestNeighbor')
# project 2 subspace
project = os.path.join(tmp_out,'T1w4nn_proj.nii.gz')
print('######################################################################')
print('6. project 2 subspace')
if not os.path.exists(project):
    patch_size = [[50,91,42,159,39,103],[91, 132,42, 159,39,103]]
    V_L = torch.load(f'../checkpoint/subspace/V_L.pt',map_location='cpu', weights_only=False)
    V_R = torch.load(f'../checkpoint/subspace/V_R.pt',map_location='cpu', weights_only=False)
    nii2subspace(preseg,project,V_L,V_R,patch_size,rank = 20)

# uncertainity estimate
print('######################################################################')
print('7. uncertainity estimate')
seg_path = os.path.join(output_path,'step_4_Tissue_Segmentation_synthseg')
os.makedirs(seg_path,exist_ok=True)

data_dir = os.path.join(save_ChP_Seg,'data_dir')
os.makedirs(data_dir,exist_ok=True)

shutil.copy(brain, os.path.join(data_dir,'chp_0000.nii.gz'))

ChP_Seg = os.path.join(tmp_out,'ChP_Seg.nii.gz')
synthseg = os.path.join(seg_path,'synthseg.nii.gz')
CSF_Seg = os.path.join(seg_path,'CSF_Seg.nii.gz')
if not os.path.exists(synthseg):
    os.system(f'mri_synthseg --i {N4} --o {synthseg} --cpu')
    os.system(f'mri_vol2vol --mov {synthseg} --targ {N4} --regheader --o {seg_path}/synthseg2T1w.nii.gz --nearest')
    os.system(f'mri_binarize  --i {seg_path}/synthseg2T1w.nii.gz --match 4 5 43 44 --o {CSF_Seg}')
            
proj = os.path.join(data_dir,'chp_0001.nii.gz')
proj_path = os.path.join(tmp_out,'proj_path.nii.gz')
proj_path_affine = os.path.join(tmp_out,'proj_path_affine.nii.gz')


os.system(f'antsApplyTransforms -d 3 -i {project} -r {brain} -o {proj} -t [{T1w2mni0GenericAffine}, 1 ]')
os.system(f'antsApplyTransforms -d 3 -i {preseg} -r {brain} -o {ChP_Seg} -t [{T1w2mni0GenericAffine}, 1 ] -n NearestNeighbor')
os.system(f'antsApplyTransforms -d 3 -i {chp_atlas} -r {brain} -o {proj_path} -t [{T1w2mni0GenericAffine}, 1 ] -t {T1w2mni1InverseWarp} -n NearestNeighbor')

uncertainity = os.path.join(data_dir,'chp_0002.nii.gz')
if not os.path.exists(uncertainity):
    make_uncertainity(brain,CSF_Seg,ChP_Seg,uncertainity,proj_path,brain_mask)

os.system(f'rm -r {tmp_out}')
os.system(f'rm -r {tmp_path}')

# # inference by chp net
x_0001 = os.path.join(data_dir,'chp_0000.nii.gz')
x_0002 = os.path.join(data_dir,'chp_0001.nii.gz')
x_0003 = os.path.join(data_dir,'chp_0002.nii.gz')

img_nii  = nib.load(brain)
msk_nii  = nib.load(brain_mask)
img      = img_nii.get_fdata()
msk      = msk_nii.get_fdata()
affine   = img_nii.affine
img_crop = img * msk
nib.save(nib.Nifti1Image(img_crop, affine, img_nii.header), x_0001)

proj_nii = nib.load(x_0002).get_fdata()
img_crop = proj_nii * msk
nib.save(nib.Nifti1Image(img_crop, affine, img_nii.header), x_0002)

proj_nii = nib.load(x_0003).get_fdata()
img_crop = proj_nii * msk
nib.save(nib.Nifti1Image(img_crop, affine, img_nii.header), x_0003)
print('######################################################################')
print('8 inference by the uncertainity-guided fusion network')
save_chp = os.path.join(save_ChP_Seg,'ChP')
os.makedirs(save_chp,exist_ok=True)

mode = 'ours_tini'
if not os.path.exists(f'{save_chp}/chp.nii.gz'):
    if gpu == '-1':
        os.system(f'OMP_NUM_THREADS=1 /opt/conda/envs/nn/bin/nnUNetv2_predict -i {data_dir} -o {save_chp} -d 603 -c {mode} -device cpu')
    else:
        os.system(f'OMP_NUM_THREADS=1 CUDA_VISIBLE_DEVICES={gpu} /opt/conda/envs/nn/bin/nnUNetv2_predict -i {data_dir} -o {save_chp} -d 603 -c {mode}')

os.system(f'rm -r {data_dir}')

if args.analysis:
    print('######################################################################')
    print('9. analysis the segmentation results')
    stats = os.path.join(save_ChP_Seg,'stats')
    os.makedirs(stats,exist_ok=True)
    seg_path = os.path.join(output_path,'step_4_Tissue_Segmentation_synthseg')
    os.makedirs(seg_path,exist_ok=True)
    synthseg = os.path.join(seg_path,'synthseg.nii.gz')
    if not os.path.exists(synthseg):
        os.system(f'mri_synthseg --i {N4} --o {synthseg} --cpu')
        os.system(f'mri_vol2vol --mov {synthseg} --targ {N4} --regheader --o {seg_path}/synthseg2T1w.nii.gz --nearest')
    ref_path = f'{seg_path}/synthseg2T1w.nii.gz'
    chp_path = f'{save_chp}/chp.nii.gz'
    output = f'{save_chp}/chp4aseg.nii.gz'
    chp_refine(ref_path, chp_path, output)
    compute_chp_volume_surface(output, json_output_path=os.path.join(stats,'stats.json'), left_label=31, right_label=63)



    
    