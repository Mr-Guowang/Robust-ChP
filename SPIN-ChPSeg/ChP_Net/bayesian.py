# The original Bayesian classifier is easily affected by initial segmentation

import numpy as np
import nibabel as nib
from sklearn.mixture import GaussianMixture


def load_nii(path):
    img = nib.load(path)
    return img.get_fdata().astype(np.float32), img.affine, img.header


def zscore_in_brain(t1w, brain_mask, p_low=0.5, p_high=99.5):
    brain_vals = t1w[brain_mask]
    brain_vals = brain_vals[np.isfinite(brain_vals)]
    if brain_vals.size == 0:
        raise ValueError("The voxels in the brain are either empty or all non finite values.")

    lo, hi = np.percentile(brain_vals, [p_low, p_high])
    inliers = brain_vals[(brain_vals >= lo) & (brain_vals <= hi)]
    if inliers.size < 10:
        inliers = brain_vals

    mu = inliers.mean()
    sigma = inliers.std(ddof=0)
    if not np.isfinite(sigma) or sigma <= 1e-8:
        sigma = brain_vals.std(ddof=0)
        if not np.isfinite(sigma) or sigma <= 1e-8:
            sigma = 1.0

    zimg = (t1w - mu) / (sigma + 1e-8)
    return zimg


def fit_single_gmm_from_mask(T1w, mask, random_state=0, reg_covar=1e-6):
    vals = T1w[mask > 0]
    vals = vals[np.isfinite(vals)].astype(np.float64).reshape(-1, 1)

    if vals.size < 10:
        raise ValueError("There are too few effective voxels in the target mask to fit.")

    gmm = GaussianMixture(
        n_components=1,
        covariance_type='full',
        reg_covar=reg_covar,
        random_state=random_state,
        max_iter=200
    ).fit(vals)

    return gmm


def normal_pdf(x, mu, sigma):
    sigma = np.maximum(sigma, 1e-8)
    return (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def gmm_pdf_1d(gmm, xs):
    weights = gmm.weights_.ravel()
    means = gmm.means_.ravel()
    vars_ = gmm.covariances_.reshape(-1)
    sigmas = np.sqrt(np.maximum(vars_, 1e-12))
    comps = [weights[k] * normal_pdf(xs, means[k], sigmas[k]) for k in range(len(weights))]
    mix = np.sum(comps, axis=0)
    return mix, comps, means, sigmas, weights


def score01_from_score_samples_single(gmm, X, shape):
    # gmm: n_components=1, covariance_type='full'
    logpdf = gmm.score_samples(X)  # log p(x)
    D = X.shape[1]
    cov = gmm.covariances_[0]
    logdet = np.linalg.slogdet(cov)[1]
    logpdf_peak = -0.5 * (D * np.log(2 * np.pi) + logdet)
    score01 = np.exp(logpdf - logpdf_peak)  # in (0,1]
    return score01.reshape(shape)


def make_uncertainity(Image, Ven_mask, ChP_Seg, save_path, proj_path, brain_mask):
    T1w, affine, header = load_nii(Image)

    brain_mask, _, _ = load_nii(brain_mask)
    brain_mask = brain_mask > 0
    T1w = zscore_in_brain(T1w, brain_mask)

    Ven_mask, _, _ = load_nii(Ven_mask)
    ven = Ven_mask > 0

    ChP_Seg, _, _ = load_nii(ChP_Seg)
    chp = ChP_Seg > 0
    other_mask = ven & (~chp)

    if chp.sum() < 10:
        raise ValueError("ChP_Seg contains too few voxels for fitting.")
    if other_mask.sum() < 10:
        raise ValueError("Ven_mask excluding ChP_Seg contains too few voxels for fitting.")

    gmm_chp = fit_single_gmm_from_mask(T1w, chp)
    gmm_other = fit_single_gmm_from_mask(T1w, other_mask)

    X = T1w.reshape(-1, 1)
    shape = T1w.shape

    likelyhood_chp1 = score01_from_score_samples_single(gmm_chp, X, shape)
    likelyhood_other = score01_from_score_samples_single(gmm_other, X, shape)

    chp_prior, _, _ = load_nii(proj_path)
    chp_prior = np.clip(chp_prior, 1e-8, 1 - 1e-8)

    denom = likelyhood_chp1 * chp_prior + likelyhood_other * (1 - chp_prior)
    denom = np.clip(denom, 1e-8, None)

    chp_posterior = (likelyhood_chp1 * chp_prior) / denom

    eps = 1e-8
    p = np.clip(chp_posterior, eps, 1 - eps)
    uncertainty_nats = -(p * np.log(p) + (1 - p) * np.log(1 - p))
    uncertainty_bits = uncertainty_nats / np.log(2)

    nib.save(nib.Nifti1Image(uncertainty_bits.astype(np.float32), affine, header), save_path)