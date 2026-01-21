# adsgen

Machine learning–driven module for adsorption structure generation and potential energy surface (PES) evaluation of molecules on surfaces.

`adsgen` is a Python tool to generate and evaluate adsorption structures of molecules on surfaces using Bayesian optimization over translations and rotations. It can be used with **foundation MACE models** to generate training datasets or with **fine-tuned MACE models** to predict adsorption geometries and energies.

---

## Introduction

This repository offers three core functionalities:

1. **Generate molecule–surface adsorption structures** using BOSS + MACE  
2. **PES exploration** for flexible molecule-surface systems (via the same interface)  
3. Convert `.traj` files to VASP input folders and compare MACE vs DFT energies for benchmarking.

This tool is meant for researchers working on molecule–surface interactions, adsorption energy landscapes, or building ML-based interatomic potentials.

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

## 1. Generate Adsorption Structures

This step runs BOSS + MACE to optimize molecular configurations on a surface.

```bash
adsgen-generate --mol molecule.xyz --surf surface.inp
```
This performs:
1. Copies molecule.xyz and surface.inp to results/
2. Runs BOSS + MACE-based optimization (surface.py)
3. Performs single-step VASP optimization on each structure (optional)

### Optional Flags
| Argument         | Description                                                             |
| ---------------- | ----------------------------------------------------------------------- |
| `--out`          | Output directory (default: `results/`)                                  |
| `--skip-vasp`    | Skip the VASP single-step optimization phase                            |
| `--vasp_command` | VASP command to run (default: `mpirun -np 4 vasp_std`)                  |
| `--nstruct`      | Total number of structures to generate                                  |
| `--initpts`      | Explicit number of initial BO points (overrides default logic)          |
| `--iterpts`      | Explicit number of iterative BO steps (overrides default logic)         |
| `--opt-dims`     | Optimization dimensions: any of `x`, `y`, `z`, `alpha`, `beta`, `gamma` |
| `--bounds-x`     | Lower and upper bounds for x-shift (e.g., `--bounds-x 0 4.07`)          |
| `--bounds-y`     | Lower and upper bounds for y-shift                                      |
| `--bounds-z`     | Lower and upper bounds for z-shift                                      |
| `--bounds-alpha` | Lower and upper bounds for α rotation (degrees)                         |
| `--bounds-beta`  | Lower and upper bounds for β rotation (degrees)                         |
| `--bounds-gamma` | Lower and upper bounds for γ rotation (degrees)                         |
| `--model_path`   | Custom MACE model path (optional)                                       |


Examples
```bash
adsgen-generate \
  --mol molecule.xyz \
  --surf surface.inp \
  --nstruct 50 \
  --opt-dims x y alpha beta \
  --bounds-x 0 4.07 \
  --bounds-y 0 4.07 \
  --bounds-alpha 0 359 \
  --bounds-beta 0 359 \
  --vasp_command "srun vasp_std"
```

This outputs:
- results/initial_configurations.xyz: Structures from BOSS+MACE
- results/4D_optimization_trajectory.traj: Trajectory of optimizations
- results/training_data_mace_opt.xyz: Combined data file (input to VASP)
- results/training_data_vasp_opt.xyz: (Only if VASP is run) DFT-optimized version

The name of the .traj file automatically reflects the number of optimization dimensions.

---

## 2. Convert .traj to VASP Input Folders

```bash
adsgen-vaspgen --traj results/4D_optimization_trajectory.traj
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

---

## HB238/hBN adsorption
The folder finetuned_models/ contains three fine-tuned MACE models and their training/test datasets for HB238 molecule adsorbed on hBN surface:

- MACE-1M/: Trained on 1M base data

- MACE-1M2M/: Extended training on 2M

- MACE-1M2M+C/: Includes additional configurations with constraints

You can run structure optimization or PES evaluation on similar systems by using the --model_path flag with one of these fine-tuned models.
