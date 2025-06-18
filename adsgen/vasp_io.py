from ase.io import read, write
import os
import shutil

def traj_to_vasp_inputs(traj_path, output_dir="vasp_inputs"):
    """
    Converts MACE optimized trajectory to VASP input folders.

    Requires:
        - INCAR, KPOINTS, and POTCAR present in the current working directory.
    """

    required_files = ["INCAR", "KPOINTS", "POTCAR"]
    for f in required_files:
        if not os.path.exists(f):
            raise FileNotFoundError(f"❌ Required file '{f}' not found in current directory.")

    os.makedirs(output_dir, exist_ok=True)
    images = read(traj_path, index=":")

    for i, atoms in enumerate(images):
        folder = os.path.join(output_dir, f"conf_{i:03d}")
        os.makedirs(folder, exist_ok=True)

        # Write POSCAR
        poscar_path = os.path.join(folder, "POSCAR")
        write(poscar_path, atoms, format="vasp")
        
        # Copy user-supplied INCAR, KPOINTS, POTCAR into each folder
        for f in required_files:
            shutil.copy(f, os.path.join(folder, f))

    print(f"📁 Created {len(images)} VASP input folders in '{output_dir}' with POSCAR, INCAR, KPOINTS, POTCAR.")

