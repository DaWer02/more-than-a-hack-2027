# Technical Report: Ball Possession Inference Pipeline

**Team Name:** Mama Doain Aku Sukses Ya (`Mama_Doain_Aku_Sukses_Ya`)  
**Team Members (3–5 Registered):** `[Complete 3–5 registered member names prior to form upload]`  
**Public Repository URL:** `[Insert public GitHub repository URL prior to form upload]`  
**Competition:** More Than a Hack 2027 — Phase 1: Ball Possession  
**Match:** FC Barcelona vs Athletic Club (`BAR-ATH`), 199,319 tactical video frames (25 FPS)  
**Deliverable File:** `outputs/Mama_Doain_Aku_Sukses_Ya.csv` (`SHA-256: 59f0cff74f3fa39df74c9bae3f724c9d9ef3d4dc8f3ebdb695e0d9ba6190a914`)

---

## 1. Approach and Architecture

### 1.1 Why Not Frame-by-Frame Classification Alone?
Independent frame-by-frame possession predictors (whether geometric proximity rules or black-box ML classifiers) suffer from two structural failures in automated football analytics:
1. **High-Frequency Temporal Chatter:** Micro-oscillations between `H`, `A`, and `D` split continuous possessions into hundreds of short fragments, devastating the official ranking metric (`spellF1`), which evaluates one-to-one temporal IoU overlap of intact possession episodes.
2. **Domain Physics & Rule Compliance:** A transient deflection is physically distinct from controlled possession, and players walking during an injury stoppage or pre-kickoff setup must resolve to Dead Ball (`D`) rather than the nearest standing player. Furthermore, competition rules strictly prohibit training, fitting, or calibrating algorithms on the provided video or ground-truth possession data.

### 1.2 System Architecture Overview
We architected a 100% deterministic, zero-training-on-match, physics-informed algorithmic pipeline comprising four coordinated subsystems plus an integrated reporting module:

```text
[ Tactical Video (ROI) ] + [ Tactical ATD Tracking ] + [ Homography Matrices ]
                         │
                         ▼
        ┌──────────────────────────────────┐
        │ 1. Multi-Sensor Ball Fusion      │
        │    - Top-Hat CV in 256x256 ROI   │
        │    - 2D Kalman Filter            │
        │    - RTS Backward Smoother       │
        └─────────────────┬────────────────┘
                          │ Fused Trajectory (x, y, vx, vy)
                          ▼
        ┌──────────────────────────────────┐   ┌───────────────────────────┐
        │ 2. Feature Extraction Engine     │◄──┤ Tactical Smart Tagging    │
        │    - Metric Player Distances     │   │ - Attacking/Defending Pol │
        │    - Kinematics & Stillness      │   │ - Goal & Kickoff Windows  │
        │    - Pitch Boundary Margins      │   └───────────────────────────┘
        └─────────────────┬────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│ 3. Dead-Ball Engine (D)  │    │ 4. Controlled Possession (HA)│
│    - Out-of-Bounds Check │    │    - Exponential Proximity   │
│    - Collective Stillness│    │    - Anti-Deflection Dwell   │
│    - Pre-Kickoff & Goal  │    │    - State Persistence       │
└─────────┬────────────────┘    └──────────────┬───────────────┘
          │ Log-Evidence S_D                   │ Log-Evidence S_H, S_A
          └───────────────┬────────────────────┘
                          ▼
        ┌──────────────────────────────────┐
        │ 5. Softmax Emission Generator    │
        │    P(H), P(A), P(D) per frame    │
        └─────────────────┬────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────┐
        │ 6. 3-State HMM Viterbi Decoder   │
        │    - Per-Half Decoding (P_stay)  │
        │    - 60-Frame Majority Filter    │
        └─────────────────┬────────────────┘
                          │
                          ▼
   Final Submission CSV (199,319 rows) + Manifest + Local Storytelling Report
```

---

## 2. Match Assets Used and Dropped

### 2.1 Utilized Assets
| Asset Name | File | Role & Usage |
|---|---|---|
| **Tactical Tracking (ATD Raw)** | `BAR-ATH_tactical_atd.txt` | 199,319 frames (`video_frame = frame_id - 1`) of 2D player and ball coordinates across 46 track slots, scaled to `105.3 x 68.0 m`. Ball visible on 113,488 frames (`56.9%`). |
| **Tactical Metadata (ATD Meta)** | `BAR-ATH_tactical_atd.xml` | FIFA/EPTS XML metadata assigning each slot to Home (`Barcelona`) or Away (`Atletic Club`). |
| **Tactical Homography** | `BAR-ATH_tactical_homography.csv` | 199,319 projective `3x3` matrices (`mean reprojection_error = 0.42 px`) for metric pitch conversion (`unproject_to_metres`) and ROI projection (`project`). |
| **Tactical Smart Tagging** | `BAR-ATH_tactical_smart_tagging.xml` | 638 SportsCode intervals mapped cleanly with polarity: offensive codes bolster the tagged team (`prior_h`/`prior_a`), defensive codes bolster the opponent, and `SET PIECES` / `GOALS` guide stoppage context. |
| **Tactical Video** | `BAR-ATH_tactical.mp4` | 1080p 25 FPS stream decoded in-memory in contiguous chunks during active missing-ATD segments (`player_mean_spd >= 1.5 m/s`), cropping a `256 x 256 px` ROI to extract Morphological Top-Hat ball candidates (10,792 detections at `conf >= 0.40`). |

### 2.2 Dropped Assets
- **Broadcast Video & Broadcast ATD (`BAR-ATH_broadcast.*`):** Dropped entirely. Broadcast uses a distinct, unsynchronized timeline (164,488 frames vs 199,319 tactical frames), contains camera cuts and slow-motion replays, and has only 65.8% usable homography coverage. Aligning it risks boundary drift across graded transitions, whereas the tactical stream is the official frame-index authority.

---

## 3. Training Data, Pretrained Models & Compliance

- **No External Labelled Training Data Used:** Zero external labelled football datasets and zero neural-network / supervised ML checkpoints were used in the final submission pipeline (`cv/ball_detector.py` runs purely classical OpenCV morphological filtering and geometry projections).
- **Zero Training or Tuning on Match Video / Ground Truth:** In strict compliance with `RULES.md` and the organizers' rules clarification, **zero algorithms or parameters were trained, fitted, or calibrated on the `BAR-ATH` video or ground-truth possession data** (including the public 5-minute window).
- **Zero Manual Labels or Cloud AI Uploads:** Zero manual annotations or human corrections were made, and zero match assets were uploaded to third-party cloud AI services.
- **Physical Domain Constants (`configs/final.yaml`):** All constants originate from standard association football physics and geometry:
  - Pitch dimensions: `105.3 x 68.0 m` at `25.0 FPS`
  - Kalman physical speed outlier gating: `45.0 m/s` (`162 km/h`), max coasting: `25` frames (`1.0 s`)
  - Kalman noise covariances: `Q = diag([0.15, 0.15, 4.0, 4.0])`, `R_ATD = diag([0.25, 0.25])`, `R_CV_BASE = diag([0.64, 0.64])` (scaled by `reprojection_error` and `cv_conf`)
  - Player control radius: `2.5 m`; anti-deflection dwell threshold: `25` frames (`1.0 s`)
  - Player walking stillness threshold: `1.35 m/s` (`4.86 km/h`)

---

## 4. Possession, Loose-Ball & Dead-Ball Rules Implemented

### 4.1 Multi-Sensor Fusion (`src/fusion/kalman_fusion.py`)
1. When ATD and CV agree within `< 3.0 m`, both measurements are fused via inverse-covariance weighting. When they disagree, the observation closer to the Kalman prediction is chosen.
2. When only ATD is available, implied frame-to-frame jumps `> 45.0 m/s` are rejected as outliers and coasted.
3. Short detection gaps are coasted up to `25` frames and smoothed backward per half using the **Rauch–Tung–Striebel (RTS) Smoother**, yielding `108,764 / 199,319` (`54.6%`) valid fused ball frames.

### 4.2 Controlled Possession vs. Loose Balls & Deflections (`src/possession/control_model.py`)
1. **Exponential Proximity & Margin:** Control scores follow $S_{\text{prox}} = \exp(-d / 2.5) \times 4.0$ plus bounded distance margin $\text{clip}((d_{\text{opp}} - d_{\text{team}}) / 2.0, -2.0, +2.0)$ and Smart Tagging directional prior (`weight = 1.2`).
2. **Anti-Deflection Dwell Filter:** An opponent challenging for the ball only wins clear possession (`frame_team`) when strictly inside `2.5 m` and `> 0.5 m` closer to the ball than the rival. A turnover is awarded **only if that opponent sustains control for `25` consecutive frames (`1.0 s`)**, preventing tackles and rebounds from shattering spells.
3. **Loose Balls & Persistence:** During passes or temporary uncertainty (`frame_team == NONE`), active team state persistence (`+2.0` log-evidence) bridges the flight for up to `35` consecutive frames (`1.4 s`) before resetting to neutral, preventing spurious flips.

### 4.3 Dead-Ball Engine (`src/possession/dead_ball.py`)
Per-frame dead-ball log-evidence $S_D$ integrates five physical signals:
1. **Out of Pitch Bounds:** When fused ball coordinates fall outside pitch boundaries (`outside_margin_m > 0.0 m`), dead-ball evidence increases by `6.0 + margin * 4.0`.
2. **Collective Player Stillness:** When mean player speed falls below `1.35 m/s` and `> 65%` of players are walking (`< 1.3 m/s`), stoppage evidence rises (`+5.0` plus speed deficit scaled by `5.0`, and `+3.0` if `< 1.0 m/s`).
3. **Missing Ball During Slow Play:** If the ball trajectory is invalid while `mean_speed < 1.5 m/s`, `S_D` rises (`+5.0`).
4. **Algorithmic Kickoff & Goal Stoppages:** Start-of-half pre-kickoff periods are detected via own-half team separation (`>= 0.80`) and low player speed (`< 1.45 m/s`, `weight = 6.0`) until an active kickoff acceleration triggers live play; post-goal celebrations (`goal_stoppage_weight = 6.0`) similarly enforce `D` until the subsequent center-circle restart.
5. **Active Sprint Suppressor:** When `mean_speed >= 1.8 m/s` near a valid ball (`< 2.5 m`), `S_D` is strongly suppressed (`-5.0`) to protect fast counter-attacks.

### 4.4 Temporal Sequence Decoding & Abstention (`src/temporal/hmm_viterbi.py`)
- **3-State HMM Viterbi:** Decoded independently per half block (`11185..90651` and `110808..190197`) in log-space over `{H, A, D}` with initial priors `[0.1, 0.1, 0.8]` and symmetric transition matrix `P(stay) = 0.996`, `P(switch) = 0.002` across all classes.
- **Post-Decoding Regularizer:** A centered `smoothing_window = 60` frame majority filter eliminates residual boundary jitter.
- **Abstention (`X`):** Assigned strictly to ungraded frames outside the two match halves (`0..11184`, `90652..110807`, `190198..199318` = `40,462` frames). Within graded play, all frames resolve to `{H, A, D}` (`H: 56,110`, `A: 38,249`, `D: 64,498`, `358` possessions, mean `10.5 s`).

---

## 5. Verification Summary & Ablation Study

Using the public 5-minute ground truth strictly as a format/alignment sanity check alongside full-match physical consistency diagnostics (`scripts/run_ablation.py`):

| Experiment | Description | Public Macro-F1 | Public Spell-F1 | Public Alive/Dead F1 | Full-Match Possessions | Mean Duration (s) |
|---|---|---|---|---|---|---|
| **E0** | Official Baseline Floor (`baseline_smooth50`) | 0.6207 | 0.3256 | 0.8990 | 669 | 7.6 s |
| **E1** | ATD Kalman Only (No CV, No RTS, Raw Proximity) | 0.5353 | 0.0027 | 0.7070 | 1,915 | 1.2 s |
| **E2** | E1 + CV Ball Candidate Detection | 0.5467 | 0.0019 | 0.7370 | 3,920 | 0.6 s |
| **E3** | E2 + RTS Backward Smoother | 0.5394 | 0.0023 | 0.7339 | 2,964 | 0.9 s |
| **E4** | E3 + Intelligent Dead-Ball Engine | 0.5611 | 0.0024 | 0.7273 | 2,934 | 0.8 s |
| **E5** | E4 + Controlled Possession Model (`dwell=25`, Argmax) | 0.7233 | 0.0626 | 0.9235 | 2,492 | 1.5 s |
| **E6** | **Mama Doain Aku Sukses Ya (Full HMM Viterbi)** | **0.7843** | **0.4000** | **0.9416** | **358** | **10.5 s** |

---

## 6. Limitations & Future Work

1. **False Positives in Classical Bright-Blob CV:** Simple Top-Hat morphological detection in `256 x 256 px` ROIs still reacts occasionally to white boots, kit highlights, or pitch markings (an internal `No-CV` check highlights how sensitive classical CV noise is around `41%` missing ATD segments). Future work would integrate a domain-general pretrained ball detector trained exclusively on external football datasets with temporal association.
2. **Severe Multi-Player Occlusions & Planar 2D Aerials:** Crowded corners and high clearances collapse to 2D pitch projections where temporary occlusion beyond `25` coasting frames creates ambiguous spatial attribution. Multi-view automatic synchronization with the broadcast camera would reduce prolonged occlusions.
3. **Explicit Spell Duration Modeling:** Replacing stationary geometric state stays in HMM with an explicit-duration Hidden Semi-Markov Model (HSMM) trained strictly on external matches could further reduce over-segmentation (`frag = 1.38` on the public window).

---

## 7. Reproduction Instructions

The pipeline is 100% deterministic (`seed = 42`) and regenerates the exact submitted CSV from the public code repository and official match bundle.

### 7.1 Environment Setup
```bash
git clone <public_repository_url>
cd more-than-a-hack-2027

# Create Python 3.12 virtual environment
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

# Install pinned pipeline dependencies
pip install -r requirements-pipeline.txt
```

### 7.2 Regenerate Exact Submission CSV
Unpack the official match assets into `./data` (or set `MTAH_DATA_DIR`). Then execute:

```bash
python run.py --config configs/final.yaml
```

This single CLI command executes steps `[1/7]` through `[8/8]`:
1. Loads match assets (`data/tactical/`) and locks seeds (`seed = 42`).
2. Performs ROI Morphological Top-Hat CV ball detection + 2D Kalman & RTS backward fusion per half (caches to `cache/tactical/`).
3. Computes kinematic/spatial features, dead-ball log-evidence, controlled possession emissions (`dwell = 25`), and 3-State HMM Viterbi decoding.
4. Writes & validates `outputs/Mama_Doain_Aku_Sukses_Ya.csv` (and mirrors it to `evaluation/results/Mama_Doain_Aku_Sukses_Ya.csv`) with deterministic checksum `SHA-256: 59f0cff74f3fa39df74c9bae3f724c9d9ef3d4dc8f3ebdb695e0d9ba6190a914`.
5. Optionally generates local Data Storytelling analytics reports (`outputs/Mama_Doain_Aku_Sukses_Ya_storytelling.{md,png,pdf}`; pass `--no-report` to skip, or `--force-recompute` to rebuild Parquet caches from scratch).

### 7.3 Validate & Run Tests
```bash
python evaluation/validate_submission.py outputs/Mama_Doain_Aku_Sukses_Ya.csv
python evaluation/run_evaluation.py
pytest
```
