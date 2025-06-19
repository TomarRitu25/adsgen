import os
import argparse
import shutil
import subprocess
from adsgen.surface import run_adsorption_optimization


def copy_file(src, dst):
    if os.path.abspath(src) != os.path.abspath(dst):
        print(f"Copying molecule: {src} → {dst}" if "xyz" in src else f"Copying surface: {src} → {dst}")
        shutil.copy(src, dst)
    else:
        print(f"⚠️ Source and destination are the same: {src}")

def run_generation(mol_path, surf_path, output_dir="results"):
    """Run full BOSS + MACE structure generation."""
    import shutil
    import subprocess

    os.makedirs(output_dir, exist_ok=True)

    mol_abs = os.path.abspath(mol_path)
    surf_abs = os.path.abspath(surf_path)

    shutil.copy(mol_abs, os.path.join(output_dir, "molecule.xyz"))
    shutil.copy(surf_abs, os.path.join(output_dir, "surface.inp"))

    print(f"✅ Copied molecule: {mol_abs} → {output_dir}/molecule.xyz")
    print(f"✅ Copied surface: {surf_abs} → {output_dir}/surface.inp")

    os.chdir(output_dir)
    print("Running BOSS + MACE training structure generation...")

    subprocess.run(["python", os.path.join(os.path.dirname(__file__), "surface.py")])



def main():
    parser = argparse.ArgumentParser(description="Generate training structures using BOSS and MACE")
    parser.add_argument("--mol", type=str, required=True, help="Path to molecule (.xyz)")
    parser.add_argument("--surf", type=str, required=True, help="Path to surface (.inp)")
    parser.add_argument("--out", type=str, default="results", help="Directory to store outputs")
    parser.add_argument("--model", type=str, default=None, help="Optional path to MACE model")
    args = parser.parse_args()
    run_generation(args.mol, args.surf, args.out, model_path=args.model)


if __name__ == "__main__":
    main()
