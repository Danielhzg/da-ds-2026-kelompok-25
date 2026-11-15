# Tata Cara Kontribusi — Kelompok 25

Ringkas; aturan lengkap dan indikator penilaian ada di [RENCANA_PROYEK.md](RENCANA_PROYEK.md).

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

Setiap anggota wajib punya PR ter-merge di sisi **DA** (`etl/`, `warehouse/`, `app/`) **dan** sisi
**DS** (`notebooks/`, `models/`). Alokasi: lihat RENCANA_PROYEK.md Bagian 3.

## Issue, label, milestone

- Setiap tugas = 1 issue dengan assignee, label (`DA`, `DS`, `Jurnal`, `Bug`, `Docs`), milestone `CP1`–`CP5`.
- Pindahkan kartu di Projects board sesuai status (Backlog → To Do → In Progress → Review → Done).

## Tag checkpoint

`v0.1-cp1` (M2) • `v0.2-cp2` (M5) • `v0.3-cp3` (M8) • `v0.4-cp4` (M11) • `v1.0-final` (M14, code freeze).

## Data & file besar

Jangan commit file >50 MB — simpan sampel + tautan sumber di `data/README.md`.
