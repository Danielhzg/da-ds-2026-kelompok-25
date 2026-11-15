# Rencana Proyek Terintegrasi Data Analitik & Data Science

> Dokumen perencanaan kelompok berdasarkan panduan *Tracking Progress Proyek – DA & DS – IT Del* (Dosen: Oppir Hutapea). Perbarui bila ada perubahan kesepakatan.

## 0. Identitas Kelompok

| | |
|---|---|
| Kelompok | **25** |
| Repositori | `da-ds-2026-kelompok-25` (privat) |
| Anggota 1 | **Dame Sisri Rumapea** (41426085) — **Ketua kelompok** + lead sisi Data Analitik. Mengambil **DASI + DALI** |
| Anggota 2 | **Daniel Haganta Ginting** (41426090) — Project Manager (menyusun laporan mingguan) + lead sisi Data Science. Mengambil **DASI** |
| Dosen | Oppir Hutapea (collaborator di GitHub) |
| Topik | **Prediksi harga cabai merah keriting di Pasar Tradisional Kota Medan** — melanjutkan hasil UTS Daniel (data PIHPS-BI 4 level pasar + cuaca Open-Meteo, 6.352 baris bersih, 10 fitur terpilih, baseline naif MAE Rp1.244) |

> Catatan pengampu: Daniel hanya mengambil DASI sehingga beban penilaiannya terutama dari sisi DS; Dame mengambil DASI + DALI sehingga memimpin sisi DA. Meski demikian, aturan **lintas lapisan** tetap berlaku untuk keduanya (lihat Bagian 3).

## 1. Ringkasan Kewajiban (hasil analisis panduan)

Empat alat pemantauan berjalan paralel dari Minggu 1 s.d. presentasi Minggu 15 (Minggu 16 = UAS):

| Alat | Kewajiban | Bukti |
|---|---|---|
| GitHub | Semua kode, data, notebook, naskah dalam 1 repo; kontribusi tiap anggota terukur | Insights > Contributors, PR, Projects board |
| Laporan mingguan | 1 laporan/minggu, M1–M14 (14 laporan), **tiap Jumat 23.59 WIB**, maks 1–2 halaman | `reports/weekly/minggu-XX.md` + tautan di LMS |
| Checkpoint | 5 checkpoint: CP1 (M2), CP2 (M5), CP3 (M8), CP4 (M11), CP5 (M15) | Tag rilis `v0.1-cp1` … `v1.0-final` + demo |
| Naskah jurnal | 1 artikel ilmiah siap submit di M15 | folder `paper/` + Lembar Jurnal Target |

**Aturan kontribusi yang wajib dipatuhi:**

- Commit dari akun GitHub masing-masing (email git = email akun GitHub).
- Minimal **2 commit bermakna per anggota per minggu** mulai M3.
- **Conventional Commits** + nomor issue: `feat:`, `fix:`, `data:`, `docs:`, `refactor:`, `paper:` — contoh `feat: tambah dim_waktu (#12)`.
- **Tidak ada push langsung ke `main`** — semua lewat pull request, PR menautkan issue (`Closes #12`).
- Setiap PR direview minimal 1 anggota lain; tiap anggota **mereview ≥1 PR per minggu**.
- Kerja berpasangan → tambahkan `Co-authored-by: Nama <email>` di pesan commit.
- **Lintas lapisan wajib**: Dame harus punya PR ter-merge di sisi DS, Daniel di sisi DA (sudah dialokasikan di Bagian 3–4).
- Tag checkpoint: `v0.1-cp1`, `v0.2-cp2`, `v0.3-cp3`, `v0.4-cp4`, `v1.0-final` (M14). **Code freeze M14** — setelah itu hanya bug kritis dengan persetujuan dosen.

**Indikator kontribusi yang dinilai dosen:**

| Indikator | Batas wajar |
|---|---|
| Porsi commit per anggota | Tidak ada anggota di bawah 15% total commit (target kami: masing-masing 40–60%) |
| Minggu aktif | Aktif ≥10 dari 13 minggu (M3–M15) |
| PR di-merge | ≥6 per anggota, mencakup sisi DA **dan** DS |
| Review | ≥1 review per anggota per minggu |
| Sebaran waktu | Tidak menumpuk dalam 48 jam sebelum checkpoint |

**Red flag yang harus dihindari:** satu akun >50% commit • commit "Add files via upload" berisi banyak file • anggota tanpa commit 2 minggu berturut-turut • commit menumpuk dekat checkpoint • nama/email commit tidak terhubung ke akun anggota.

**Bobot penilaian:** CP1 10% • CP2 10% • CP3 15% • CP4 15% • laporan mingguan 10% • CP5 25% • naskah jurnal 15%.
**Nilai individu** = nilai kelompok × faktor kontribusi (0,6–1,0); faktor = data GitHub 40% + peer assessment 30% + tanya jawab presentasi 30%.

## 2. Setup Repositori

- [x] Struktur folder wajib dibuat (`data/ etl/ warehouse/ notebooks/ models/ app/ paper/ reports/weekly/ docs/`)
- [x] Data, notebook, dan dokumen hasil UTS dimigrasi ke repo
- [x] README: judul, anggota + peran, cara menjalankan
- [x] `.gitignore` + `CONTRIBUTING.md` (aturan kontribusi)
- [ ] Repo privat `da-ds-2026-kelompok-25` dibuat di GitHub → push
- [ ] Undang dosen + Dame sebagai collaborator
- [ ] Pastikan `git config user.email` Dame = email akun GitHub-nya
- [ ] Protect branch `main` (Settings > Branches): wajib PR + minimal 1 approval
- [ ] GitHub Projects board: kolom **Backlog, To Do, In Progress, Review, Done**
- [ ] Label: `DA`, `DS`, `Jurnal`, `Bug`, `Docs`; milestone: `CP1`–`CP5`
- [ ] Backfill tag `v0.1-cp1`, `v0.2-cp2`, `v0.3-cp3` pada commit yang sesuai (lihat catatan Bagian 4)

## 3. Pembagian Peran

| Peran | Dame (Ketua) | Daniel (PM) |
|---|---|---|
| Ketua / koordinasi kelompok | ✅ | – |
| Penyusun laporan mingguan | – | ✅ (setiap anggota tetap mengisi baris kontribusinya sendiri) |
| Sisi DA: `etl/`, `warehouse/`, `app/` dashboard | ✅ lead | kontribusi lintas lapisan |
| Sisi DS: `notebooks/` model, `models/` | kontribusi lintas lapisan | ✅ lead |
| Naskah jurnal | lead Pembahasan + Kesimpulan + referensi (Zotero) | lead Pendahuluan + Metode + Hasil |
| Review PR | ≥1/minggu (review PR Daniel) | ≥1/minggu (review PR Dame) |

**Alokasi lintas lapisan (agar syarat "PR di kedua sisi" terpenuhi):**
- Daniel → PR sisi DA: `docs/data-dictionary`, definisi KPI dashboard, halaman storytelling di `app/`.
- Dame → PR sisi DS: fungsi feature pipeline di `etl/` yang dipakai model, `models/model-card.md`, visual error-analysis.

## 4. Rencana Mingguan M1–M15

*Kalender: M1 = 14–20 Sep 2026 → M9 (berjalan) = 9–15 Nov 2026. Sesuaikan dengan kalender akademik. Laporan jatuh tiap Jumat 23.59 WIB.*

| Mg | Status | Fokus | Tugas Dame | Tugas Daniel | Deliverable / bukti |
|---|---|---|---|---|---|
| 1 (14–20/9) | lampau | Kick-off | Peran & board | Repo & aturan | `reports/weekly/minggu-01.md` *(terlewat)* |
| 2 (21–27/9) | lampau | **CP1 Proposal** | KPI dashboard + profil pengguna (TPID, pedagang) + ide judul | Pertanyaan analitik + metrik (MAE/RMSE/MAPE; target < baseline naif Rp1.244) | `docs/proposal.md`; tag `v0.1-cp1` *(backfill)* |
| 3 (28/9–4/10) | lampau | Akuisisi data | `docs/data-dictionary.md` + verifikasi jurnal target + 10 referensi | Kajian model serupa (ARIMA/RF/GBM) + 10 referensi | `paper/jurnal-target.md`; 20 referensi Zotero |
| 4 (5–11/10) | lampau | EDA | Laporan kualitas data; agregat siap-dashboard | Notebook 01–02; kelayakan fitur & target | `notebooks/`; `docs/log_cleaning.csv`; tinjauan pustaka |
| 5 (12–18/10) | lampau | **CP2 Data readiness** | DDL skema bintang + `etl/` + ERD | Fitur kandidat; draf Pendahuluan | `warehouse/`, `etl/`; tag `v0.2-cp2` *(backfill)* |
| 6 (19–25/10) | lampau | Dashboard v1 | Wireframe + skeleton `app/` + chart KPI | Feature engineering + split (nb 03) | `app/`; `notebooks/03` |
| 7 (26/10–1/11) | lampau | Baseline | Visual analisis; hubungkan app ke warehouse | Baseline naif + pembanding linear; draf Metode | `notebooks/baseline` |
| 8 (2–8/11) | lampau | **CP3 (UTS)** | Dashboard v1 terhubung warehouse + demo | Laporan baseline; Pendahuluan+Metode draf 1 | Demo; tag `v0.3-cp3` *(backfill)* |
| **9 (9–15/11)** | **berjalan** | Visualisasi advance | Drill-down + cross-filter dashboard | Model lanjutan + tuning (RF/GBM); desain eksperimen | PR model lanjutan; experiment log |
| 10 (16–22/11) | rencana | Evaluasi | `models/model-card.md` + halaman storytelling + tabel/gambar hasil | Evaluasi + error analysis; teks storytelling | `models/model-card.md`; tabel & gambar hasil |
| 11 (23–29/11) | rencana | **CP4 Prototipe** | Visual hasil model di dashboard | API/modul prediksi + integrasi model ke app | Prototipe terintegrasi; tag `v0.4-cp4`; draf Hasil |
| 12 (30/11–6/12) | rencana | Deployment & uji | Uji kegunaan 3–5 pengguna; draf Pembahasan | Deploy app + uji input baru | URL aplikasi di README; hasil uji pengguna |
| 13 (7–13/12) | rencana | Draf lengkap | Perbaikan UI dari hasil uji + checklist author guidelines | Perbaikan model + konsolidasi naskah | `paper/draf-lengkap` dikirim ke dosen |
| 14 (14–20/12) | rencana | Finalisasi | Freeze aplikasi + laporan akhir + dokumentasi model | Revisi naskah + cek similarity (≤20%) + README final | Tag `v1.0-final`; **code freeze**; laporan similarity |
| 15 (21–27/12) | rencana | **CP5 Presentasi** | Presentasi + demo + tanya jawab | Presentasi + demo + tanya jawab | Naskah final + semua deliverable |

**Catatan posisi (M9):** repo efektif berdiri di M9. Deliverable M1–M8 sudah ada sebagai hasil UTS dan **dimigrasi ke repo ini lewat PR per topik** (data → EDA → FE → seleksi → warehouse), bukan satu commit besar "Add files via upload". Tag `v0.1-cp1` s.d. `v0.3-cp3` di-backfill pada commit migrasi yang sesuai. Laporan M1–M8 yang terlewat → **konfirmasi ke dosen** apakah boleh susulan; bila ya, isi ringkas dengan bukti commit migrasi yang ada. Yang pasti: mulai M9 laporan rutin tiap Jumat tanpa terlewat.

## 5. Ritme Kerja Mingguan (SOP)

| Hari | Aktivitas |
|---|---|
| Sen–Rab | Kerjakan issue masing-masing di branch sendiri; commit bertahap (≥2 commit bermakna per orang) |
| Rab–Kam | Buka PR → saling review → revisi → merge (`Closes #issue`) |
| Jum | Update kartu board; isi `reports/weekly/minggu-XX.md` lewat PR; kirim tautan ke LMS **sebelum 23.59 WIB** |
| Sab–Min | Buffer / sesi berpasangan (`Co-authored-by`); rapikan backlog minggu depan |

**Konvensi branch:** `feat/…`, `fix/…`, `data/…`, `docs/…`, `paper/…` — satu branch per issue.
**Contoh commit:** `feat(app): tambah halaman KPI harga harian (#17)` • `data(etl): impor PIHPS pedagang besar (#9)` • `fix(model): koreksi leakage lag-1 (#24)` • `paper: draf bagian metode (#21)`

## 6. Rencana Naskah Jurnal

| Aspek | Keputusan / rencana |
|---|---|
| Jalur | **B — SINTA 1–3** (disarankan: lebih realistis untuk tim 2 orang; Lembar Jurnal Target di `paper/jurnal-target.md` — wajib difinalkan, normalnya batas M3 → kejar segera) |
| Kandidat kebaruan | dataset lokal baru (harga cabai 4 level pasar Medan + cuaca), perbandingan model perubahan harga, sistem terintegrasi dashboard+prediksi |
| Bahasa | Indonesia/Inggris sesuai ketentuan jurnal terpilih |
| Struktur | Abstrak, Pendahuluan, Metode, Hasil, Pembahasan, Kesimpulan (+ sesuai template jurnal) |
| Referensi | ≥20 (Jalur B); ≥80% jurnal/prosiding; mayoritas <5 tahun; dikelola di **Zotero** (rencana: 8 model time-series/pangan, 5 dashboard/BI, 4 warehouse/ETL, 3 konteks cabai-pangan Indonesia) |
| Similarity | ≤20% — dicek M14, laporan disimpan di `paper/` |
| Penulis | Dame, Daniel, dosen pengampu — urutan disepakati (usulan: ketua sebagai penulis pertama) |
| Jadwal bagian | jurnal target → kejar finalisasi M9 → tinjauan pustaka M10 → Metode+Hasil M10–M11 → Pembahasan M12 → draf lengkap M13 → revisi+similarity M14 → final M15 |

## 7. Status, Risiko & Mitigasi

**Status kelompok** (diisi di tiap laporan): 🟢 sesuai timeline & semua aktif • 🟡 tertinggal ±1 minggu / 1 anggota kurang aktif → wajib rencana pemulihan tertulis • 🔴 tertinggal >1 minggu / anggota tidak commit 2 minggu → wajib asistensi dosen.

| Risiko | Mitigasi |
|---|---|
| Tim hanya 2 orang — bila satu sakit/minggu sibuk, red flag "tanpa commit" terpicu | Sesi berpasangan dengan `Co-authored-by`; buffer M13; kabari dosen lebih awal bila ada kendala |
| Daniel hanya mengambil DASI → kontribusi sisi DA bisa terlupakan | Tugas lintas lapisan Daniel sudah dialokasikan (Bagian 3); dicek tiap Jumat |
| Pekerjaan UTS lama di-push sekaligus → commit menumpuk | Migrasi bertahap lewat PR per topik (data → EDA → FE → seleksi → warehouse) |
| Satu orang mendominasi commit | Board membagi issue rata di awal minggu; cek `git shortlog -sne --no-merges` tiap Jumat |
| File data/model >50 MB | Simpan sampel + tautan saja; `.gitignore` untuk data besar |
| Angka di naskah ≠ hasil di repo | Semua tabel/gambar naskah dihasilkan ulang dari notebook (single source of truth) |

## 8. Checklist Cepat Setiap Jumat (sebelum kirim laporan)

- [ ] Kedua anggota punya ≥2 commit minggu ini (cek Insights > Contributors)
- [ ] Minimal 1 PR ter-merge per orang, sudah saling review
- [ ] Kartu board dipindah sesuai status
- [ ] `reports/weekly/minggu-XX.md` terisi lengkap + bukti bertautan (commit/PR/issue)
- [ ] Tautan laporan dikirim ke LMS < 23.59 WIB

---

## Lampiran A — Template Laporan Mingguan

Tersedia siap pakai di `reports/weekly/_template.md` — salin menjadi `minggu-XX.md` tiap minggu.

## Lampiran B — Lembar Jurnal Target

Tersedia di `paper/jurnal-target.md` — lengkapi dan lampirkan tangkapan layar verifikasi SINTA.
