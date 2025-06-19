import os
from ase.io import read, write
from ase.optimize.precon import PreconLBFGS
from ase.calculators.vasp import Vasp


def run_single_step_optimization(skip_vasp=False, vasp_command="mpirun -np 4 vasp_std"):
    mace_xyz = "training_data_mace_opt.xyz"
    output_xyz = "training_data_vasp_opt.xyz"

    if not os.path.exists(mace_xyz):
        raise FileNotFoundError(f"❌ Missing required file: {mace_xyz}")

    if skip_vasp:
        print(f"⚠️ Skipping VASP optimization. Output: {mace_xyz}")
        return

    structures = read(mace_xyz, index=":")
    optimized_structures = []

    for i, atoms in enumerate(structures):
        workdir = f"vasp_opt_{i}"
        os.makedirs(workdir, exist_ok=True)
        os.chdir(workdir)

        write("POSCAR", atoms)

        atoms.calc = Vasp(
            command=vasp_command,
            encut=400,
            kpts=[1, 1, 1],
            ediff=1e-4,
            nsw=1,
            ibrion=2,
            isif=2,
            lwave=False,
            lcharg=False,
            istart=0,
            nelm=100,
        )

        try:
            opt = PreconLBFGS(atoms, maxstep=0.05)
            opt.run(fmax=0.05, steps=1)
            optimized_structures.append(atoms)
            print(f"✅ Optimized structure {i}")
        except Exception as e:
            print(f"❌ Optimization failed for structure {i}: {e}")

        os.chdir("..")

    if optimized_structures:
        write(output_xyz, optimized_structures)
        print(f"\n✅ All VASP-optimized structures saved to '{output_xyz}'")
    else:
        print("⚠️ No successful optimizations.")

