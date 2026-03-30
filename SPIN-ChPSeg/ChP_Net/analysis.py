import os
import json
import nibabel as nib
import numpy as np
from skimage.measure import marching_cubes


def chp_refine(ref_path, chp_path, output):
    ref_nii = nib.load(ref_path)
    ref_data = np.round(ref_nii.get_fdata()).astype(np.int16)

    chp_nii = nib.load(chp_path)
    chp_data = np.round(chp_nii.get_fdata()).astype(np.int16)

    data = np.zeros_like(chp_data, dtype=np.int16)
    left_hemisphere_mask = (ref_data > 0) & (ref_data < 40)
    right_hemisphere_mask = (ref_data >= 40)

    chp_mask = (chp_data == 1)

    data[chp_mask & left_hemisphere_mask] = 31
    data[chp_mask & right_hemisphere_mask] = 63

    new_nii = nib.Nifti1Image(data, chp_nii.affine, chp_nii.header)
    nib.save(new_nii, output)


def _compute_surface_area_from_mask(mask, spacing):
    """
    mask: 3D bool array
    spacing: (sx, sy, sz) in mm
    return: surface area in mm^2
    """
    if mask.sum() == 0:
        return 0.0

    if mask.sum() < 4:
        return 0.0

    try:
        verts, faces, _, _ = marching_cubes(
            mask.astype(np.uint8),
            level=0.5,
            spacing=spacing
        )
    except Exception:
        return 0.0

    if faces.shape[0] == 0:
        return 0.0

    tri = verts[faces]  # (N, 3, 3)
    a = tri[:, 1] - tri[:, 0]
    b = tri[:, 2] - tri[:, 0]
    area = 0.5 * np.linalg.norm(np.cross(a, b), axis=1)
    return float(area.sum())


def compute_chp_volume_surface(
    chp_label_path,
    json_output_path=None,
    left_label=31,
    right_label=63
):

    nii = nib.load(chp_label_path)
    data = np.round(nii.get_fdata()).astype(np.int16)

    spacing = nii.header.get_zooms()[:3]  # mm
    voxel_volume_mm3 = float(np.prod(spacing))

    left_mask = (data == left_label)
    right_mask = (data == right_label)
    total_mask = left_mask | right_mask

    left_voxels = int(left_mask.sum())
    right_voxels = int(right_mask.sum())
    total_voxels = int(total_mask.sum())

    left_volume_mm3 = float(left_voxels * voxel_volume_mm3)
    right_volume_mm3 = float(right_voxels * voxel_volume_mm3)
    total_volume_mm3 = float(total_voxels * voxel_volume_mm3)

    left_surface_mm2 = _compute_surface_area_from_mask(left_mask, spacing)
    right_surface_mm2 = _compute_surface_area_from_mask(right_mask, spacing)
    total_surface_mm2 = _compute_surface_area_from_mask(total_mask, spacing)

    result = {
        "voxel_volume_mm3": voxel_volume_mm3,

        "left_voxels": left_voxels,
        "right_voxels": right_voxels,
        "total_voxels": total_voxels,

        "left_volume_mm3": left_volume_mm3,
        "right_volume_mm3": right_volume_mm3,
        "total_volume_mm3": total_volume_mm3,

        "left_surface_mm2": left_surface_mm2,
        "right_surface_mm2": right_surface_mm2,
        "total_surface_mm2": total_surface_mm2,
    }

    if json_output_path is not None:
        os.makedirs(os.path.dirname(json_output_path), exist_ok=True) if os.path.dirname(json_output_path) else None
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    return result