"""Unit tests for CV ball candidate detection and Parquet caching behavior."""

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.cv.ball_detector import BallCandidateDetector, extract_cv_ball_table, TOTAL_FRAMES


def test_ball_candidate_detector_bright_blob():
    """Verify Top-Hat contour filtering detects a clean ball-like synthetic bright blob."""
    matrix = np.eye(3, dtype=np.float64)
    # Map norm [0, 1] -> approx [0..1053, 0..680] inside crop range
    matrix[0, 0] = 1000.0
    matrix[1, 1] = 680.0
    detector = BallCandidateDetector(np.repeat(matrix[None, :, :], 5, axis=0))

    crop = np.full((128, 128, 3), 30, dtype=np.uint8)
    # Draw crisp white 8px circular blob around (64, 64)
    yy, xx = np.ogrid[:128, :128]
    mask = ((xx - 64) ** 2 + (yy - 64) ** 2) <= 16
    crop[mask] = 240

    cand = detector.detect_candidate_in_crop(crop, roi_x=200, roi_y=150, matrix=matrix)
    assert cand is not None
    assert abs(cand["u_px"] - 264.0) <= 2.5
    assert abs(cand["v_px"] - 214.0) <= 2.5
    assert cand["confidence"] >= 0.4


def test_extract_cv_ball_table_respects_use_cache(tmp_path):
    """Verify use_cache=False bypasses stale Parquet cache when recomputing."""
    parquet_path = tmp_path / "cv_ball.parquet"
    stale_df = pd.DataFrame({
        "video_frame": np.arange(TOTAL_FRAMES, dtype=np.int32),
        "detected": np.ones(TOTAL_FRAMES, dtype=bool),
        "u_px": np.zeros(TOTAL_FRAMES, dtype=np.float32),
        "v_px": np.zeros(TOTAL_FRAMES, dtype=np.float32),
        "pitch_x_m": np.zeros(TOTAL_FRAMES, dtype=np.float32),
        "pitch_y_m": np.zeros(TOTAL_FRAMES, dtype=np.float32),
        "cv_conf": np.ones(TOTAL_FRAMES, dtype=np.float32),
        "bbox_w": np.zeros(TOTAL_FRAMES, dtype=np.float32),
        "bbox_h": np.zeros(TOTAL_FRAMES, dtype=np.float32),
        "reproj_err": np.zeros(TOTAL_FRAMES, dtype=np.float32),
    })
    pq.write_table(pa.Table.from_pandas(stale_df), parquet_path)

    zeros_m = np.zeros((TOTAL_FRAMES, 2), dtype=np.float32)
    zeros_b = np.zeros(TOTAL_FRAMES, dtype=bool)
    zeros_f = np.zeros(TOTAL_FRAMES, dtype=np.float32)

    cached_df = extract_cv_ball_table(
        decoder=None, homography_matrices=None, reprojection_errors=zeros_f,
        atd_ball_pos_m=zeros_m, atd_ball_vis=zeros_b, player_mean_spd=zeros_f,
        output_parquet_path=str(parquet_path), cv_enabled=False, use_cache=True,
    )
    assert bool(cached_df["detected"].all())

    fresh_df = extract_cv_ball_table(
        decoder=None, homography_matrices=None, reprojection_errors=zeros_f,
        atd_ball_pos_m=zeros_m, atd_ball_vis=zeros_b, player_mean_spd=zeros_f,
        output_parquet_path=str(parquet_path), cv_enabled=False, use_cache=False,
    )
    assert not bool(fresh_df["detected"].any())
