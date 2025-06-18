# adsgen

**adsgen** is a Python package for generating and analyzing adsorption training structures using:

- 🎯 [BOSS](https://github.com/SINGROUP/boss): for Bayesian optimization of molecular poses
- 🧠 [MACE](https://github.com/ACEsuit/mace): for machine-learned energy evaluations
- ⚛️ VASP: for validating DFT-level adsorption energies

This toolkit helps automate the generation of training structures and comparison of learned vs DFT energies for systems like organic molecules on metal surfaces.

---

## 📦 Features

- Generate adsorption structures using BOSS + MACE
- Convert optimized `.traj` to VASP-ready folders
- Compare MACE and DFT energies with RMSE/MAE
- Export visualizations and side-by-side CSV outputs

---

## 🗂️ Project Structure

adsgen/
├── adsgen/ # Python module
│ ├── generator.py # Structure generation
│ ├── structure_io.py # CLI for traj → VASP folders
│ ├── vasp_io.py # Writes POSCAR and copies VASP inputs
│ ├── plotting.py # boss.rst → energy plot
│ ├── analysis.py # Compare energies and compute metrics
│ └── config.py # (optional defaults)
├── data/ # Molecule + surface input files
├── results/ # Generated results (.traj, .png, .txt)
├── scripts/ # (optional) bash wrappers
├── setup.py
├── .gitignore
└── README.md


---

## 🚀 CLI Commands

After installing, you get 3 commands:

### 1. Generate Adsorption Structures

```bash
adsgen-generate --mol data/HB238.xyz --surf data/Ag.inp

    Outputs:

        results/boss.rst

        results/5D_optimization_trajectory.traj

        results/initial_configurations.xyz

        results/boss_energy_vs_step.png

2. Convert .traj to VASP Input Folders

adsgen-vaspgen --traj results/5D_optimization_trajectory.traj

    This creates:

    vasp_inputs/conf_000/
      ├── POSCAR
      ├── INCAR
      ├── KPOINTS
      └── POTCAR

    ⚠️ Requires:
    Place INCAR, KPOINTS, and POTCAR in the current working directory before running this command.

3. Compare MACE and DFT Energies

adsgen-compare \
  --traj results/5D_optimization_trajectory.traj \
  --dft-dir vasp_inputs \
  --out results/E0_comparison_plot.png

    Generates:

        mace_extracted_energies.txt

        dft_extracted_energies.txt

        E0_comparison_plot.png

        E0_comparison_plot.csv

    Prints: RMSE and MAE values to terminal

🧰 Installation

git clone https://github.com/YOUR_USERNAME/adsgen.git
cd adsgen
pip install -e .

📦 Requirements

    Python 3.9+

    Packages: ase, numpy, matplotlib

    External (not bundled):

        BOSS (for structure search)

        MACE (for ML energy evaluation)

        VASP (for DFT energy validation)

