import numpy as np
from boss.bo.bo_main import BOMain
from boss.pp.pp_main import PPMain
from ase.io import read, write, Trajectory
from ase.constraints import FixAtoms
from ase.build import rotate
from mace.calculators import mace_mp
from ase.parallel import parprint
import matplotlib.pyplot as plt
import os
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

log_file = 'optimization_log.txt'
with open(log_file, 'w', encoding='utf-8') as log:
    log.write("Step-by-step Optimization Log\n")
    log.write("=" * 50 + "\n")

# Global list to store results
results = []

def safe_parprint(*args):
    """Safe printing to handle UnicodeEncodeError"""
    try:
        parprint(*args)
    except UnicodeEncodeError as e:
        parprint(f"UnicodeEncodeError: {e}. Logging in safe mode.")
        parprint(str(args).encode('ascii', 'replace').decode())

def log_step(step, energy, x_shift, y_shift, alpha, beta, gamma):
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"Step {step}:\n")
        log.write(f"x_shift: {x_shift:.4f} A, y_shift: {y_shift:.4f} A\n")
        log.write(f"Alpha: {alpha:.2f} degrees, Beta: {beta:.2f} degrees, Gamma: {gamma:.2f} degrees\n")
        log.write(f"Energy: {energy:.6f} eV\n")
        log.write("-" * 50 + "\n")

def func(X):
    x_shift, y_shift, alpha, beta, gamma = map(float, X.ravel())  # Unpack the 5D variables
    try:
        atoms = read('surface.inp', format='vasp')
        constraint = FixAtoms(indices=[atom.index for atom in atoms])
        atoms.set_constraint(constraint)

        H6 = read('molecule.xyz')

        # Perform rotations first
        center_of_mass = H6.get_center_of_mass()
        H6.rotate(alpha, 'z', center=center_of_mass)
        H6.rotate(beta, 'y', center=center_of_mass)
        H6.rotate(gamma, 'x', center=center_of_mass)

        # After rotation, calculate the minimum z-coordinate of H6
        min_z_H6_rotated = min(atom.position[2] for atom in H6)
        max_surface_z = max(atom.position[2] for atom in atoms)

        # Apply lateral shifts
        H6.translate([x_shift, y_shift, 0.0])

        # Fix z-height based on the rotated H6's min_z
        height_adjustment = max_surface_z + 2.5 - min_z_H6_rotated
        H6.translate([0, 0, height_adjustment])

        atoms.extend(H6)

        # Save the initial configuration before optimization
        write(initial_xyz_file, atoms, append=True)

        from mace.calculators import MACECalculator
        calc = mace_mp(model="medium", default_dtype="float64", device='cuda',  weights_only=True)
        atoms.set_calculator(calc)

        from ase.optimize.precon import Exp, PreconLBFGS
        opt = PreconLBFGS(atoms, use_armijo=True, precon=None, variable_cell=False, trajectory='opt.traj')
        opt.run(fmax=0.01)

        safe_parprint(f"Optimization complete for x_shift={x_shift:.4f}, y_shift={y_shift:.4f}, alpha={alpha:.2f}, beta={beta:.2f}, gamma={gamma:.2f}")
        safe_parprint(f"Total Energy: {atoms.get_total_energy():.6f} eV")

        for atom in atoms:
            safe_parprint(atom)

        safe_parprint(atoms.get_cell()[:])

        energy = atoms.get_potential_energy()
        if not np.isfinite(energy):
            raise ValueError(f"Non-finite energy value: {energy}")

        # Log and save results
        results.append((x_shift, y_shift, alpha, beta, gamma, energy))
        step = len(results)
        log_step(step, energy, x_shift, y_shift, alpha, beta, gamma)
        trajectory.write(atoms)
        return float(energy)

    except Exception as e:
        safe_parprint(f"Optimization failed at x={x_shift:.4f}, y={y_shift:.4f}, alpha={alpha:.2f}, beta={beta:.2f}, gamma={gamma:.2f}: {e}")
        return np.inf

def plot_results(results, output_file):
    # Sort results by energy
    results = sorted(results, key=lambda x: x[5])
    energies = [r[5] for r in results]
    steps = list(range(1, len(energies) + 1))

    plt.figure(figsize=(8, 6))
    plt.plot(steps, energies, marker='o', linestyle='-', label='Energy')
    plt.xlabel('Optimization Step')
    plt.ylabel('Energy (eV)')
    plt.title('Energy vs Optimization Steps')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Graph saved to {output_file}")

traj_file = '5D_optimization_trajectory.traj'
open(traj_file, 'w').close()  # Ensure file is empty
trajectory = Trajectory(traj_file, 'w')

initial_xyz_file = 'initial_configurations.xyz'
open(initial_xyz_file, 'w').close()  # Ensure file is empty

print("Running on CPU.")

# Bounds for x_shift, y_shift, alpha, beta, and gamma
bounds = np.array([
    [0, 4.07],   # x_shift range
    [0, 4.07],   # y_shift range
    [0, 359],     # alpha rotation range
    [0, 359],     # beta rotation range
    [0, 359]      # gamma rotation range
])

bo = BOMain(func, bounds, kernel=['stdp', 'stdp', 'rbf', 'rbf', 'rbf'], initpts=20, iterpts=980, parallel_optims=16)

res = bo.run()
optimal_params = res.select('X', -1)[0]
optimal_energy = res.select('mu_glmin', -1)

print(f"Optimal parameters: x_shift={optimal_params[0]:.4f} A, y_shift={optimal_params[1]:.4f} A, alpha={optimal_params[2]:.2f} degrees, beta={optimal_params[3]:.2f} degrees, gamma={optimal_params[4]:.2f} degrees")
print(f"Minimum potential energy: {optimal_energy:.6f} eV")

output_graph_file = 'adsorption_energy_vs_steps.png'
plot_results(results, output_graph_file)

try:
    pp = PPMain(res, pp_models=True, pp_acq_funcs=True)
    pp.run()
except Exception as e:
    safe_parprint(f"Post-processing failed: {e}")

trajectory.close()
print(f"Optimization complete. Results saved in {traj_file}.")
print(f"Log file created: {log_file}")

