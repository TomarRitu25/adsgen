# adsgen

Machine learning–driven training structure generator for adsorption on surfaces.

adsgen is a Python tool that generates training structures for molecule–surface systems using a 5D Bayesian optimization (x, y shifts + α, β, γ rotations) with:

- BOSS: Bayesian Optimization Structure Search

- MACE: Machine Learning Potential

- (Optional) VASP: Single-step DFT optimization

It outputs optimized training structures suitable for building machine-learned interatomic potentials.

---

## Introduction

This repository contains three key functionalities:

1. Generation of adsorption structures using BOSS + MACE
2. Conversion of optimized `.traj` files to VASP-ready input folders (for explicit VASP optimization)
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
This performs:
1. Copies molecule.xyz and surface.inp to results/
2. Runs BOSS + MACE-based optimization (surface.py)
3. Performs single-step VASP optimization on each structure (optional)

### Optional Flags
| Flag             | Description                                                        |
| ---------------- | ------------------------------------------------------------------ |
| `--out`          | Output directory (default: `results/`)                             |
| `--skip-vasp`    | Skip the single-step VASP optimization step                        |
| `--vasp_command` | Custom command for running VASP (default: `mpirun -np 4 vasp_std`) |


Examples
```bash
adsgen-generate --mol molecule.xyz --surf surface.inp
adsgen-generate --mol molecule.xyz --surf surface.inp --skip-vasp
adsgen-generate --mol molecule.xyz --surf surface.inp --vasp_command "srun vasp_std"
```

This outputs:
- results/initial_configurations.xyz: Structures from BOSS+MACE
- results/5D_optimization_trajectory.traj: Trajectory of optimizations
- results/training_data_mace_opt.xyz: Combined data file (input to VASP)
- results/training_data_vasp_opt.xyz: (Only if VASP is run) DFT-optimized version

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
