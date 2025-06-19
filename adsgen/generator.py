import os
import argparse
from pathlib import Path
from adsgen.surface import run_boss_mace
from adsgen.vasp_single_step_opt import run_single_step_optimization

def run_generation(mol_path, surf_path, output_dir="results", skip_vasp=False, vasp_command="mpirun -np 4 vasp_std"):
    """Main function to run the full training structure generation pipeline."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    mol_dst = output_dir / "molecule.xyz"
    surf_dst = output_dir / "surface.inp"

    # Copy molecule
    if Path(mol_path).resolve() != mol_dst.resolve():
        os.system(f"cp {mol_path} {mol_dst}")
        print(f"✅ Copied molecule: {mol_path} → {mol_dst}")
    else:
        print(f"⚠️ Source and destination are the same: {mol_path}")

    # Copy surface
    if Path(surf_path).resolve() != surf_dst.resolve():
        os.system(f"cp {surf_path} {surf_dst}")
        print(f"✅ Copied surface: {surf_path} → {surf_dst}")
    else:
        print(f"⚠️ Source and destination are the same: {surf_path}")

    # Run surface optimization (BOSS + MACE)
    print("Running BOSS + MACE training structure generation...")
    run_boss_mace(mol_dst, surf_dst, output_dir)

    # Optionally run VASP optimization
    run_single_step_optimization(skip_vasp=skip_vasp, vasp_command=vasp_command)


def main():
    parser = argparse.ArgumentParser(description="Generate training data using BOSS + MACE and optional VASP optimization")
    parser.add_argument("--mol", type=str, required=True, help="Path to molecule.xyz")
    parser.add_argument("--surf", type=str, required=True, help="Path to surface.inp")
    parser.add_argument("--out", type=str, default="results", help="Output directory (default: results)")
    parser.add_argument("--skip-vasp", action="store_true", help="Skip VASP single-step optimization")
    parser.add_argument("--vasp_command", type=str, default="mpirun -np 4 vasp_std", help="VASP command to use (default: mpirun -np 4 vasp_std)")

    args = parser.parse_args()
    run_generation(args.mol, args.surf, args.out, args.skip_vasp, args.vasp_command)


if __name__ == "__main__":
    main()

