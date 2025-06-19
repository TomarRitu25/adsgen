import numpy as np
from boss.bo.bo_main import BOMain
from boss.pp.pp_main import PPMain
from ase.io import read, write, Trajectory
from ase.constraints import FixAtoms
from ase.build import rotate
from ase.parallel import parprint
from ase.optimize.precon import PreconLBFGS
from mace.calculators import MACECalculator
import matplotlib.pyplot as plt
import os
import warnings
import torch
import shutil

warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

log_file = 'optimization_log.txt'
initial_xyz_file = 'initial_configurations.xyz'
traj_file = '5D_optimization_trajectory.traj'
output_graph_file = 'adsorption_energy_vs_steps.png'

results = []
trajectory = Trajectory(traj_file, 'w')

def safe_parprint(*args):
    try:
        parprint(*args)
    except UnicodeEncodeError as e:
        parprint(f"UnicodeEncodeError: {e}. Logging in safe mode.")
        parprint(str(args).encode('ascii', 'replace').decode())

def log_step(step, energy, x_shift, y_shift, alpha, beta, gamma):
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"Step {step}:\n")
        log.write(f"x_shift: {x_shift:.4f} A, y_shift: {y_shift:.4f} A\n")
        log.write(f"Alpha: {alpha:.2f}°, Beta: {beta:.2f}°, Gamma: {gamma:.2f}°\n")
        log.write(f"Energy: {energy:.6f} eV\n")
        log.write("-" * 50 + "\n")

def get_mace_calculator(user_model_path=None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Running on {device.upper()}.")

    fallback_model = os.path.join(os.path.dirname(__file__), "models", "2023-12-03-mace-128-L1_epoch-199.model")
    cache_model = os.path.expanduser("~/.cache/mace/models/2023-12-03-mace-128-L1_epoch-199.model")

    if user_model_path and os.path.exists(user_model_path):
        model_path = user_model_path
        print(f"Using user-provided MACE model: {model_path}")
    elif os.path.exists(cache_model):
        model_path = cache_model
        print(f"Using cached MACE model: {model_path}")
    elif os.path.exists(fallback_model):
        model_path = fallback_model
        print(f"⚠️ Download failed. Using fallback MACE model: {model_path}")
    else:
        raise FileNotFoundError("❌ No MACE model found in cache, fallback, or user path.")

    return MACECalculator(model_path=model_path, device=device, default_dtype="float64")

def func(X):
    x_shift, y_shift, alpha, beta, gamma = map(float, X.ravel())

    try:
        atoms = read('surface.inp', format='vasp')
        atoms.set_constraint(FixAtoms(indices=[atom.index for atom in atoms]))

        mol = read('molecule.xyz')
        center = mol.get_center_of_mass()
        mol.rotate(alpha, 'z', center=center)
        mol.rotate(beta, 'y', center=center)
        mol.rotate(gamma, 'x', center=center)

        min_z = min(atom.position[2] for atom in mol)
        max_z = max(atom.position[2] for atom in atoms)
        mol.translate([x_shift, y_shift, 0.0])
        mol.translate([0, 0, max_z + 2.5 - min_z])

        atoms.extend(mol)
        write(initial_xyz_file, atoms, append=True)

        atoms.set_calculator(func.calc)
        opt = PreconLBFGS(atoms, use_armijo=True, precon=None, variable_cell=False, trajectory='opt.traj')
        opt.run(fmax=0.01)

        energy = atoms.get_potential_energy()
        if not np.isfinite(energy):
            raise ValueError("Non-finite energy")

        step = len(results) + 1
        results.append((x_shift, y_shift, alpha, beta, gamma, energy))
        log_step(step, energy, x_shift, y_shift, alpha, beta, gamma)
        trajectory.write(atoms)
        return float(energy)

    except Exception as e:
        safe_parprint(f"Optimization failed at x={x_shift:.4f}, y={y_shift:.4f}, "
                      f"alpha={alpha:.2f}, beta={beta:.2f}, gamma={gamma:.2f}: {e}")
        return np.inf

def plot_results(results, output_file):
    results = sorted(results, key=lambda x: x[5])
    energies = [r[5] for r in results]
    steps = list(range(1, len(energies) + 1))

    plt.figure(figsize=(8, 6))
    plt.plot(steps, energies, marker='o')
    plt.xlabel('Optimization Step')
    plt.ylabel('Energy (eV)')
    plt.title('Energy vs Optimization Steps')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Saved plot to {output_file}")

def run_adsorption_optimization(model_path=None):
    with open(log_file, 'w') as f:
        f.write("Step-by-step Optimization Log\n" + "=" * 50 + "\n")

    open(initial_xyz_file, 'w').close()
    trajectory = Trajectory(traj_file, 'w')

    func.calc = get_mace_calculator(user_model_path=model_path)

    bounds = np.array([
        [0, 4.07], [0, 4.07], [0, 359], [0, 359], [0, 359]
    ])

    bo = BOMain(func, bounds, kernel=['stdp', 'stdp', 'rbf', 'rbf', 'rbf'],
                initpts=20, iterpts=980, parallel_optims=16)

    res = bo.run()
    opt_params = res.select("X", -1)[0]
    opt_energy = res.select("mu_glmin", -1)

    print(f"\n Optimal x={opt_params[0]:.2f}, y={opt_params[1]:.2f}, "
          f"alpha={opt_params[2]:.1f}, beta={opt_params[3]:.1f}, gamma={opt_params[4]:.1f}")
    print(f"Minimum energy: {opt_energy:.6f} eV")

    plot_results(results, output_graph_file)

    try:
        PPMain(res, pp_models=True, pp_acq_funcs=True).run()
    except Exception as e:
        safe_parprint(f"⚠️ Postprocessing failed: {e}")

    trajectory.close()
    print(f"Trajectory saved to {traj_file}")
    print(f"Log saved to {log_file}")

