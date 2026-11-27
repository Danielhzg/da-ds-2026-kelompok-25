# Tata Cara Kontribusi — Kelompok 25

Pedoman ringkas kolaborasi GitHub untuk menjaga konsistensi kode, keterlacakan isu, dan keseimbangan kontribusi antar anggota.

## Branch & PR

- Tidak ada push langsung ke `main`. Satu issue = satu branch.
- Penamaan: `feat/…`, `fix/…`, `data/…`, `docs/…`, `paper/…`, `refactor/…`.
- PR menautkan issue dengan `Closes #<nomor>` dan deskripsi singkat perubahan.
- Minimal 1 approval sebelum merge. Setiap anggota mereview ≥1 PR per minggu.

## Commit

- Format **Conventional Commits** + nomor issue:
  `feat: tambah dim_waktu (#12)` — tipe: `feat`, `fix`, `data`, `docs`, `refactor`, `paper`, `chore`.
- Minimal **2 commit bermakna per anggota per minggu**; hindari menumpuk mendekati checkpoint.
- Kerja berpasangan: tambahkan trailer
  `Co-authored-by: Nama <email>` agar kedua anggota tercatat.
- Dilarang commit "Add files via upload" berisi banyak file sekaligus — migrasi/kerja lewat PR per topik.

## Lintas lapisan

Setiap anggota wajib punya PR ter-merge di sisi **DA** (`etl/`, `warehouse/`, `app/`, `docs/data-dictionary.md`) **dan** sisi **DS** (`notebooks/`, `models/`):
- **Dame Sisri Rumapea (41426085):** Lead sisi DA (`warehouse/`, `etl/`, dashboard `app/app.py` & `01..03`) + kontribusi DS (`models/model-card.md`).
- **Daniel Haganta Ginting (41426090):** Lead sisi DS (`notebooks/06-07`, `models/`, `app/pages/04_Prediksi_Harga.py`) + kontribusi DA (`docs/data-dictionary.md`).

## Issue, label, milestone

- Setiap tugas = 1 issue dengan assignee, label (`DA`, `DS`, `Jurnal`, `Bug`, `Docs`), milestone `CP1`–`CP5`.
- Pindahkan kartu di Projects board sesuai status (Backlog → To Do → In Progress → Review → Done).

## Tag checkpoint

`v0.1-cp1` (M2) • `v0.2-cp2` (M5) • `v0.3-cp3` (M8) • `v0.4-cp4` (M11) • `v1.0-final` (M14, code freeze).

## Data & file besar

Jangan commit file >50 MB — simpan sampel + tautan sumber di `data/README.md`.
