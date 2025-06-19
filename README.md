# adsgen

Machine learning–driven training structure generator for adsorption on surfaces.

This program enables the generation of adsorption geometries using Bayesian optimization with BOSS and a pretrained MACE machine learning potential. It also provides tools to convert these geometries into VASP input folders and compare MACE-predicted energies against DFT values using RMSE, MAE, and energy plots.

---

## Introduction

This repository contains three key functionalities:

1. Generation of adsorption structures using BOSS + MACE
2. Conversion of optimized `.traj` files to VASP-ready input folders
3. Energy comparison between MACE and DFT using a plotting and CSV export tool

The goal is to assist in generating large, diverse, and relevant training datasets for ML potential development, particularly for molecule–surface systems.

---

## Installation

Clone and install in development mode:

```bash
git clone https://github.com/TomarRitu25/adsgen.git
cd adsgen
pip install -e .
pip install aalto-boss
pip install git+https://github.com/ACEsuit/mace.git
```
---

## 1. Generate Training Structures

This step runs BOSS + MACE to optimize molecular configurations on a surface.

```bash
adsgen-generate --mol molecule.xyz --surf surface.inp
```

This produces:
- results/boss.rst
- results/5D_optimization_trajectory.traj
- results/initial_configurations.xyz
- results/boss_energy_vs_step.png

---

## 2. Convert .traj to VASP Input Folders

```bash
adsgen-vaspgen --traj results/5D_optimization_trajectory.traj
```
**Note:** You must place the INCAR, KPOINTS and POTCAR files in the current working directory before running this command

---

## 3. Compare MACE and DFT Energies

After you run DFT calculations in the vasp_inputs/conf_* folders, you can compare the energies using:
```bash
adsgen-compare --traj results/5D_optimization_trajectory.traj --dft-dir vasp_inputs --out results/E0_comparison_plot.png
```

This generates:
- mace_extracted_energies.txt
- dft_extracted_energies.txt
- E0_comparison_plot.png
- E0_comparison_plot.csv

---

## Requirements
- Python ≥ 3.10 (required for aalto-boss)
- PyTorch (compatible version required for mace-torch)
- External: VASP (not bundled - licence required)
