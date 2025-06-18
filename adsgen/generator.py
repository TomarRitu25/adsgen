import os
import argparse
from adsgen.plotting import plot_energy_from_rst


def run_generation(mol_path, surf_path, output_dir="results"):
    """Main function to run the training structure generation pipeline."""

    os.makedirs(output_dir, exist_ok=True)

    print(f"Copying molecule: {mol_path} → data/molecule.xyz")
    os.system(f"cp {mol_path} data/molecule.xyz")

    print(f"Copying surface: {surf_path} → data/surface.inp")
    os.system(f"cp {surf_path} data/surface.inp")

    print("Running BOSS + MACE training structure generation...")
    run_boss_mace()

    rst_file = os.path.join(output_dir, "boss.rst")
    traj_file = os.path.join(output_dir, "5D_optimization_trajectory.traj")

    if os.path.exists(rst_file):
        print("Plotting energy vs. step using boss.rst")
        plot_energy_from_rst(rst_file, os.path.join(output_dir, "boss_energy_vs_step.png"))
    else:
        print("⚠️ boss.rst not found — skipping plot.")

    if os.path.exists(traj_file):
        print(f"Final trajectory written to {traj_file}")
    else:
        print("⚠️ Final trajectory file not found!")


def main():
    parser = argparse.ArgumentParser(description="Generate training structures using BOSS and MACE")
    parser.add_argument("--mol", type=str, required=True, help="Path to molecule (.xyz)")
    parser.add_argument("--surf", type=str, required=True, help="Path to surface (.inp or .xyz)")
    parser.add_argument("--out", type=str, default="results", help="Directory to store outputs")
    args = parser.parse_args()
    run_generation(args.mol, args.surf, args.out)


if __name__ == "__main__":
    main()

