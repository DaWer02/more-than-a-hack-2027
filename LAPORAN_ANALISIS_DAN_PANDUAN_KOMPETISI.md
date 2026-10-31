# LAPORAN ANALISIS MENDALAM & PANDUAN STRATEGIS LOMBA
## "MORE THAN A HACK 2027" (FC Barcelona & Metrica Sports)

---

## DAFTAR ISI
1. [Ringkasan Eksekutif & Identitas Kompetisi](#1-ringkasan-eksekutif--identitas-kompetisi)
2. [Definisi Masalah & Ruang Lingkup Prediksi](#2-definisi-masalah--ruang-lingkup-prediksi)
3. [Anatomi Dataset & Tantangan Kunci](#3-anatomi-dataset--tantangan-kunci)
4. [Sistem Evaluasi & Rahasia Metrik spellF1](#4-sistem-evaluasi--rahasia-metrik-spellf1)
5. [Analisis Baseline Resmi & Bukti Empiris](#5-analisis-baseline-resmi--bukti-empiris)
6. [Aturan Main & Batasan Legalitas (Rules of Engagement)](#6-aturan-main--batasan-legalitas-rules-of-engagement)
7. [Arsitektur Solusi Rekomendasi (Engineering Pipeline)](#7-arsitektur-solusi-rekomendasi-engineering-pipeline)
8. [Panduan Eksekusi Tim & Pembagian Peran](#8-panduan-eksekusi-tim--pembagian-peran)
9. [Checklist Final Submission](#9-checklist-final-submission)

---

## 1. RINGKASAN EKSEKUTIF & IDENTITAS KOMPETISI

* **Penyelenggara Resmi**: Metrica Sports, FC Barcelona (Barça Innovation Hub), dan Mobile World Capital Barcelona.
* **Pertandingan Subjek**: FC Barcelona vs Athletic Club (`BAR-ATH`) — Laga La Liga berdurasi penuh.
* **Tenggat Waktu (Submission Deadline)**: **17 November 2026**.
* **Persyaratan Peserta**: Tim wajib beranggotakan **3 hingga 5 orang** yang terdaftar secara sah.
* **Format Output**: Menghasilkan satu file CSV prediksi (`frame,label`) sebanyak **199.319 baris**, disertai repositori kode publik dan dokumen teknis ringkas (PDF/MD).
* **Metrik Penentu Peringkat**: **`spellF1`** (Temporal IoU mean matching), didukung oleh `macroF1` sebagai *tie-break*.

---

## 2. DEFINISI MASALAH & RUANG LINGKUP PREDIKSI

### 2.1 Spesifikasi Frame
* **Total Frame**: **199.319 frame** pada **25 Frame Per Second (FPS)** (~2 jam 12 menit total rekaman).
* **Frame Dinilai (Graded Gameplay)**: Sebanyak **158.857 frame** (~106 menit permainan aktif) yang mencakup babak pertama dan babak kedua.
* **Frame Tidak Dinilai**: Frame sebelum kick-off babak 1, jeda istirahat babak pertama (halftime, 20.156 frame), dan setelah peluit akhir.

### 2.2 Taksonomi Label Prediksi (4 Simbol)
| Label | Nama Lengkap | Definisi Operasional Resmi |
| :---: | :--- | :--- |
| **`H`** | **Home in Possession** | FC Barcelona menguasai bola dan bola dalam status hidup (*alive / in-play*). |
| **`A`** | **Away in Possession** | Athletic Club menguasai bola dan bola dalam status hidup (*alive / in-play*). |
| **`D`** | **Dead Ball** | Bola mati / pertandingan berhenti (*stoppage*): bola keluar lapangan (throw-in, goal kick, corner), pelanggaran, selebrasi gol, sebelum kick-off/restart. |
| **`X`** | **Abstain / Ungraded** | Model abstain / menolak menebak, atau frame berada di luar rentang evaluasi. |

### 2.3 Aturan Kepemilikan Bola (Possession Rules)
1. **Bola Selalu Dimiliki Selama Hidup**: Tidak ada kelas "contested", "loose", atau "transition". Selama bola dinyatakan hidup oleh wasit, bola secara sah **selalu dimiliki oleh tim terakhir yang mengontrolnya**.
2. **Definisi Pergantian Penguasaan (*Turnover / Change of Possession*)**:
   * Hanya terjadi jika pemain lawan berhasil melakukan **kontrol nyata** terhadap bola.
   * *Bukan Turnover*: Sentuhan sekilas tanpa kontrol, defleksi bola, tekel yang memantul, atau memenangkan duel udara tanpa penguasaan lanjutan oleh tim tersebut.
3. **Dead Ball Bukan Penguasaan**:
   * Bola mati (`D`) adalah penghentian laga (*stoppage*), bukan bagian dari penguasaan tim manapun. Pelacakan tracking sering mengaitkan bola mati dengan tim yang akan mengambil lemparan/tendangan, namun ground truth resmi mengabaikannya dan menetapkannya murni sebagai `D`.

---

## 3. ANATOMI DATASET & TANTANGAN KUNCI

Semua data tersimpan di bawah folder `data/` dengan hierarki berikut:

```
data/
├── tactical/                                (TIMELINE ACUAN RESMI 1:1)
│   ├── BAR-ATH_tactical.mp4                 Video sudut lebar statis 25 FPS
│   ├── BAR-ATH_tactical_atd.xml             Metadata tracking FIFA/EPTS
│   ├── BAR-ATH_tactical_atd.txt             Koordinat x, y, speed pemain & bola
│   ├── BAR-ATH_tactical_homography.csv      Matriks proyeksi 3x3 ke lapangan (meter)
│   └── BAR-ATH_tactical_smart_tagging.xml   638 anotasi taktis otomatis (fase laga)
└── broadcast/                               (OPSIONAL - TIDAK SINKRON)
    ├── BAR-ATH_broadcast.mp4                Video siaran televisi (multi-kamera)
    ├── BAR-ATH_broadcast_atd.xml            Tracking kamera broadcast
    ├── BAR-ATH_broadcast_atd.txt
    └── BAR-ATH_broadcast_homography.csv
```

### 3.1 Detail Data Tracking (ATD)
* Format per baris: `<frame>:<player_0>;...;<player_45>:<ball_x,ball_y,speed>`.
* Terdapat **46 slot tracklet** untuk 22 pemain yang ada di lapangan.
* **Penting**: Nomor tracklet (`Track 1` s.d. `Track 46`) adalah slot pelacakan otomatis, bukan nomor punggung atau ID pemain permanen. Posisi pemain dinormalisasi ke rentang $[0, 1]$.

### 3.2 Tiga Tantangan Tersembunyi (Hidden Pitfalls)
1. **Bola Hilang pada 41% Frame Graded (Missing Ball Problem)**:
   * Tracking bola bernilai `NaN` pada **41% durasi laga aktif** (akibat oklusi pemain, bola melayang terlalu tinggi, atau blur).
   * Algoritma baseline langsung menyerah dan mengisi `D` saat bola hilang. Ini menyebabkan fragmentasi penguasaan bola yang sangat parah.
2. **Data Smart Tagging Bersifat Heuristik (Bukan Ground Truth Mutlak)**:
   * Berisi **638 fase taktis** (Build-up, Counter-attack, Set-piece, High Press).
   * Data ini sangat berguna sebagai *prior probabilitas*, tetapi memiliki noise waktu ($\pm 1-2$ detik) dan tidak boleh diperlakukan sebagai ground truth mutlak.
3. **Public Ground Truth HANYA 5 MENIT (Jebakan Overfitting)**:
   * Panitia hanya menyediakan ground truth publik sebanyak **7.500 frame (5 menit / 17 penguasaan bola)** pada frame 11.185 s.d. 18.684 (`evaluation/gt/BAR-ATH_possession_gt_public.csv`).
   * **Peringatan Resmi**: Window ini hanya untuk memverifikasi fungsionalitas pipeline. Optimasi hyperparameter (seperti lebar window smoothing) pada 5 menit ini terbukti menghasilkan performa buruk pada Full Match 90 menit.

---

## 4. SISTEM EVALUASI & RAHASIA METRIK SPELLF1

### 4.1 Mengapa Bukan Akurasi Frame Biasa?
Sepak bola didominasi oleh segmen panjang. Sebanyak 80%+ frame berada di bagian dalam penguasaan bola yang stabil. Model yang mengalami "flickering" (berganti-ganti label H-A-H-A setiap 0,2 detik) masih bisa mendapatkan akurasi frame 90%+, namun secara analitik sepak bola model tersebut sama sekali tidak berguna karena menciptakan ratusan possession palsu.

### 4.2 Cara Kerja `spellF1` (Metrik Utama Papan Peringkat)
1. **Ekstraksi Possession Spell**:
   * Seluruh rangkaian berurutan label `H` atau `A` diekstrak sebagai sebuah interval waktu $[start, stop]$.
   * Rangkaian `D` memutus interval penguasaan.
2. **Pencocokan 1-to-1 dengan Ground Truth (Greedy IoU Matching)**:
   * Setiap spell prediksi dipasangkan dengan spell ground truth dari tim yang sama.
   * Dihitung nilai **Temporal IoU (Intersection over Union)**:
     $$\text{IoU} = \frac{\text{Durasi Irisan (Intersection)}}{\text{Durasi Gabungan (Union)}}$$
3. **Thresholding Multilevel**:
   * Dihitung Precision, Recall, dan F1 pada 5 ambang batas IoU: $\text{IoU} \in \{0.3, 0.4, 0.5, 0.6, 0.7\}$.
   * **`spellF1`** adalah nilai rata-rata (*unweighted mean*) dari kelima F1 tersebut.

### 4.3 Hirarki Penentuan Peringkat (Tie-Breaking Order)
1. **`spellF1`** (Peringkat utama).
2. **`macroF1`** (Rata-rata unweighted F1 untuk kelas H, A, D pada frame graded).
3. **`transF1`** (F1 deteksi transisi pergantian status pada toleransi $\pm 25$ frame / 1 detik).
4. **`Mean Absolute Latency`** (Keterlambatan waktu deteksi transisi).
5. **Nama File** (Deterministik jika seluruh metrik di atas identik).

---

## 5. ANALISIS BASELINE RESMI & BUKTI EMPIRIS

Panitia menyertakan kode acuan pada `starter/baseline.py` dengan logika sederhana: *Pemain terdekat dengan bola menentukan tim yang memegang bola; jika bola hilang, vonis D; lalu terapkan majority voting window.*

### Performa Baseline pada Full Match (199.319 Frame - Benchmark Resmi)
| Varian Baseline | Window Half-Width | spellF1 (Metrik Utama) | macroF1 | Karakteristik Performa |
| :--- | :---: | :---: | :---: | :--- |
| `baseline_raw` | 0 (Tanpa smoothing) | **0.0486** | 0.6532 | Bencana fragmentasi: memprediksi 6x lebih banyak possession dari aslinya. |
| `baseline_smooth25` | $\pm 1.0\text{ s}$ (25 frame) | **0.1996** | 0.6752 | Mengurangi jitter, namun masih banyak transisi semu. |
| **`baseline_smooth50`**| $\pm 2.0\text{ s}$ (50 frame) | **0.2433** | **0.6724** | **FLOOR TO BEAT RESMI** (Target minimal yang wajib dikalahkan). |
| `baseline_smooth125`| $\pm 5.0\text{ s}$ (125 frame) | **0.2242** | 0.6356 | Terlalu agresif menghapus possession pendek yang sah. |

### Bukti Jebakan Public Ground Truth (5 Menit / 17 Possessions)
Hasil eksekusi evaluasi pada file publik 5 menit menunjukkan anomali terbalik:
* `baseline_smooth125` mencatat skor tertinggi (**0.4242**) di data publik 5 menit.
* Namun di Full Match, `baseline_smooth125` justru kalah dari `baseline_smooth50` (**0.2242 vs 0.2433**).
* *Pelajaran*: Smoothing besar terlihat bagus pada sampel kecil karena kebetulan menutupi fluktuasi lokal, tetapi merusak batas temporal pada skala 90 menit.

---

## 6. ATURAN MAIN & BATASAN LEGALITAS (RULES OF ENGAGEMENT)

Agar solusi tim sah dan tidak didiskualifikasi:
* 🚫 **Dilarang Anotasi Manual (No Hand-Labeling)**: Seluruh 199.319 frame wajib dilabeli oleh kode/algoritma secara otomatis.
* 🚫 **Dilarang Menggunakan API Model Cloud dengan Data Laga**: Tidak boleh mengirim gambar frame, klip video, atau koordinat laga `BAR-ATH` ke OpenAI GPT-4V, Claude API, Gemini API komersial eksternal. (Menggunakan model open-weights yang dijalankan lokal seperti YOLO, ResNet, dll. sepenuhnya diperbolehkan).
* 🚫 **Dilarang Menggunakan Data Eksternal Laga Spesifik Ini**: Tidak boleh menggunakan feed data komersial resmi (Opta, StatsBomb, Wyscout match logs) yang secara spesifik mencatat laga Barcelona vs Athletic Club ini.
* 🚫 **Dilarang Overfitting / Hardcoding Public GT**: Dilarang membuat if-else khusus pada frame 11.185–18.684.
* ✅ **Wajib Reproducible 100%**: Panitia akan mengkloning repositori tim dan menjalankan perintah reproduksi. Hasil CSV yang dihasilkan kode wajib identik dengan file CSV yang diunggah ke formulir submission.

---

## 7. ARSITEKTUR SOLUSI REKOMENDASI (ENGINEERING PIPELINE)

Untuk mendongkrak skor `spellF1` dari **0.2433 ke target 0.4500 - 0.6000+**, arsitektur sistem yang direkomendasikan terdiri dari 4 modul berurutan:

```
[DATA MENTAH: ATD Tracking + Homography + Smart Tagging]
                          │
                          ▼
    ┌───────────────────────────────────────────┐
    │ MODUL 1: Ball Imputation & Kinematics     │
    │ • Interpolasi spline/Kalman pada gap bola │
    │ • Estimasi posisi via centroid tim saat   │
    │   bola hilang > 2 detik                   │
    └─────────────────────┬─────────────────────┘
                          │
                          ▼
    ┌───────────────────────────────────────────┐
    │ MODUL 2: Geometric & Dead-Ball Engine     │
    │ • Homografi pitch bounds (105x68 m)       │
    │   -> jika bola keluar = pasti D           │
    │ • Set-piece tags (Corner, Free kick, etc) │
    │ • Deteksi perlambatan kecepatan 22 pemain │
    └─────────────────────┬─────────────────────┘
                          │
                          ▼
    ┌───────────────────────────────────────────┐
    │ MODUL 3: Controlled Possession Estimator  │
    │ • Radius kontrol pemain terhadap bola     │
    │ • Ambang batas durasi kontrol (>= 12 fr)  │
    │ • Pertahankan tim lama saat bola loose    │
    └─────────────────────┬─────────────────────┘
                          │
                          ▼
    ┌───────────────────────────────────────────┐
    │ MODUL 4: Temporal HMM / Semi-Markov Model │
    │ • 3-State Model (H, A, D)                 │
    │ • Penalti transisi state realistis        │
    │ • Viterbi Decoding -> Anti-Flickering     │
    └─────────────────────┬─────────────────────┘
                          │
                          ▼
         [FILE HASIL AKHIR: <nama_tim>.csv]
```

### Rincian Strategi Tiap Modul:
1. **Modul 1 (Penanganan 41% Bola Hilang)**:
   * Jika bola hilang $\le 50$ frame (2 detik), lakukan interpolasi polinomial antara posisi sebelum hilang dan saat muncul kembali.
   * Hitung vektor kecepatan bola untuk membedakan operan melambung vs bola keluar.
2. **Modul 2 (Deteksi Bola Mati / D Cerdas)**:
   * Konversi koordinat bola ke meter via homografi. Jika $x < 0$, $x > 105$, $y < 0$, atau $y > 68$, tetapkan probabilitas $P(D) = 1.0$.
   * Ekstrak timestamp event bola mati dari `smart_tagging.xml` (Corner, Throw-in, Free kick). Tetapkan window jeda sebelum eksekusi sebagai `D`.
   * Saat pertandingan berhenti, kecepatan rata-rata pemain menurun drastis menjadi berjalan kaki ($< 1.5\text{ m/s}$).
3. **Modul 3 (Kontrol Nyata vs Defleksi)**:
   * Jangan langsung mengubah label jika pemain lawan berada di dekat bola hanya selama 1–3 frame.
   * Terapkan syarat *dwell time* minimal (misal: 10–15 frame berurutan) atau perubahan arah bola yang dikontrol sebelum mendeklarasikan turnover.
4. **Modul 4 (Dekode Temporal Global)**:
   * Ganti *moving majority vote* dengan **Hidden Markov Model (HMM)** atau *Semi-Markov Model*.
   * Matriks transisi menetapkan probabilitas bertahan pada status saat ini sebesar $\approx 0.98 - 0.99$, merefleksikan durasi possession nyata di sepak bola (10–20 detik). Algoritma Viterbi secara matematis memotong transisi palsu/berkedip.

---

## 8. PANDUAN EKSEKUSI TIM & PEMBAGIAN PERAN

Tim berjumlah 3–5 orang dapat membagi tugas secara paralel:

| Peran Tim | Fokus Tanggung Jawab Utama | Tool / Bahasa |
| :--- | :--- | :--- |
| **Lead / Modeling Engineer** | Membangun HMM / Temporal State Machine, merancang matriks emisi dan transisi Viterbi, tuning evaluasi `spellF1`. | Python, NumPy, SciPy |
| **Spatial & Geometry Engineer** | Mengolah matriks homografi, mendeteksi bola keluar garis, melakukan interpolasi posisi bola hilang (Kalman Filter). | Python, OpenCV, NumPy |
| **Tactical Data Engineer** | Parsing XML `smart_tagging.xml` dan `atd.xml`, memetakan event set-piece, menganalisis kecepatan pemain per tim. | Python, xml.etree, Pandas |
| **Validation & Documentation** | Menjalankan pipeline evaluasi, memvalidasi format CSV, mengelola repositori GitHub, menyusun Laporan Teknis (PDF). | Git, Markdown, LaTeX/Word |

---

## 9. CHECKLIST FINAL SUBMISSION

Sebelum mengirimkan formulir pada 17 November 2026:

- [ ] **1. File Prediksi (`<nama_tim>.csv`)**:
  - Tepat 199.319 baris data + 1 baris header (`frame,label`).
  - Kolom `frame` berurutan dari `0` sampai `199318`.
  - Nilai kolom `label` hanya berisi `H`, `A`, `D`, atau `X` (tidak ada cell kosong).
  - Lolos pengujian: `python evaluation/validate_submission.py <nama_tim>.csv` tanpa peringatan.
- [ ] **2. Repositori GitHub Publik**:
  - Memiliki `README.md` dengan instruksi instalasi dan perintah eksekusi satu baris yang jelas.
  - Memiliki `requirements.txt` dengan versi paket yang terkunci.
  - **Bebas dari aset data**: Pastikan video dan folder `data/` TIDAK ikut di-push ke GitHub.
- [ ] **3. Laporan Teknis (`<nama_tim>.pdf` atau `<nama_tim>.md`)**:
  - Penjelasan arsitektur dan metodologi algoritma.
  - Dokumentasi penggunaan aset (ATD, Homography, Smart Tagging).
  - Penjelasan aturan kontrol bola dan limitasi sistem.
  - Petunjuk reproduksi kode.
- [ ] **4. Anggota Tim**:
  - Memastikan seluruh anggota terdaftar resmi (3–5 orang).

