# adsgen

**Machine learning–driven training data generation for adsorption modeling using BOSS and MACE.**

This program enables the generation of high-quality 5D adsorption structures using Bayesian optimization (BOSS) and the MACE machine-learned potential. The goal is to accelerate the development of ML potentials for molecule–surface systems. Additionally, it includes utilities to export optimized configurations for DFT calculations and compare MACE vs. DFT energies.

---

## Introduction

This repository contains two major functionalities:

- **Structure generation pipeline** based on BOSS + MACE  
- **Energy comparison framework** between MACE and DFT

The procedure typically involves the following steps:

1. Running BOSS + MACE to optimize molecular configurations over a surface.
2. Exporting the resulting structures to VASP-compatible folders.
3. Comparing predicted MACE energies against DFT-calculated values for the same geometries.

⚠️ VASP calculations must be performed externally. The project assumes `INCAR`, `KPOINTS`, and `POTCAR` are available and copied into the working directory manually.

---

## Installation

Clone and install locally in development mode:

```bash
git clone https://github.com/TomarRitu25/adsgen.git
cd adsgen
pip install -e .

This will register the following CLI tools:

    adsgen-generate

    adsgen-vaspgen

    adsgen-compare

## Usage

**1. Generate Training Structures (BOSS + MACE)**

This step copies your molecule and surface files, runs BOSS with MACE as energy backend, and produces a .traj file with optimized geometries.

```bash
adsgen-generate --mol data/HB238.xyz --surf data/Ag.inp

Outputs:

    - results/boss.rst

    - results/boss_energy_vs_step.png

    - results/5D_optimization_trajectory.traj

    - results/initial_configurations.xyz

## **2. Convert .traj to VASP Input Folders**

Once the optimized .traj is generated, use this to create VASP input directories:

```bash
adsgen-vaspgen --traj results/5D_optimization_trajectory.traj

⚠️ **Required:** Place these files in the working directory before running:

    INCAR

    KPOINTS

    POTCAR

**Output (per structure):**
```bash
vasp_inputs/conf_000/
├── POSCAR
├── INCAR
├── KPOINTS
└── POTCAR

## **3. Compare MACE and DFT Energies**

Once DFT calculations are complete for all conf_* folders, use:

```bash
adsgen-compare \
  --traj results/5D_optimization_trajectory.traj \
  --dft-dir vasp_inputs \
  --out results/E0_comparison_plot.png

Outputs:

    - mace_extracted_energies.txt

    - dft_extracted_energies.txt

    - results/E0_comparison_plot.png

    - results/E0_comparison_plot.csv

Also prints:

    RMSE and MAE between MACE and DFT energies

**Requirements**

    - Python 3.9+

    - Dependencies:
        - ase
        - numpy
        - matplotlib

    - External tools (not bundled):
        - BOSS
        - MACE
        - VASP (must be pre-installed and licensed)


## **Citation**

This code was developed for machine-learning-assisted catalyst design involving large flexible molecules on surfaces.
Please cite relevant BOSS, MACE, and VASP references if you use this pipeline in a publication.
