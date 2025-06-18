import os
from ase.io import read
import argparse
from adsgen.vasp_io import traj_to_vasp_inputs

def load_structure(path):
    """
    Load molecule or surface from file. Supports .xyz and .vasp/.inp formats.
    """
    try:
        return read(path)
    except Exception as e:
        print(f"❌ Failed to read structure from {path}: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Convert .traj file to VASP input folders")
    parser.add_argument("--traj", type=str, required=True, help="Path to .traj file")
    parser.add_argument("--out", type=str, default="vasp_inputs", help="Output directory for VASP folders")
    parser.add_argument("--incar", type=str, help="Path to INCAR file")
    parser.add_argument("--vsub", type=str, help="Path to submission script")
    args = parser.parse_args()

    traj_to_vasp_inputs(args.traj, args.out, args.incar, args.vsub)

if __name__ == "__main__":
    main()

