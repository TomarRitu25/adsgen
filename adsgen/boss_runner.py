import os

def run_boss_mace():
    print("Running BOSS...")
    os.system("boss -i data/surface.inp")

    print("Running MACE...")
    os.system("mace_run_train --cfg data/molecule.xyz --output results/5D_optimization_trajectory.traj")

    print("Structure generation complete.")

