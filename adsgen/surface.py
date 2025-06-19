import numpy as np
from boss.bo.bo_main import BOMain
from boss.pp.pp_main import PPMain
from ase.io import read, write, Trajectory
from ase.constraints import FixAtoms
from ase.parallel import parprint
from ase.optimize.precon import PreconLBFGS
from mace.calculators import MACECalculator
import matplotlib.pyplot as plt
import os
import torch
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

results = []

def safe_parprint(*args):
    try:
        parprint(*args)
    except UnicodeEncodeError as e:
        parprint(f"UnicodeEncodeError: {e}. Logging in safe mode.")
        parprint(str(args).encode('ascii', 'replace').decode())

def log_step(step, energy, x_shift, y_shift, z_shift, alpha, beta, gamma, log_file):
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"Step {step}:\n")
        log.write(f"x: {x_shift:.2f}, y: {y_shift:.2f}, z: {z_shift:.2f}, alpha: {alpha:.2f}, beta: {beta:.2f}, gamma: {gamma:.2f}\n")
        log.write(f"Energy: {energy:.6f} eV\n")
        log.write("-" * 50 + "\n")

def get_mace_calculator(user_model_path=None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Running on {device.upper()}.")

    fallback_model = os.path.join(os.path.dirname(__file__), "models", "2023-12-03-mace-128-L1_epoch-199.model")
    cache_model = os.path.expanduser("~/.cache/mace/models/2023-12-03-mace-128-L1_epoch-199.model")

    if user_model_path and os.path.exists(user_model_path):
        model_paths = user_model_path
        print(f"Using user-provided MACE model: {model_paths}")
    elif os.path.exists(cache_model):
        model_paths = cache_model
        print(f"Using cached MACE model: {model_paths}")
    elif os.path.exists(fallback_model):
        model_paths = fallback_model
        print(f"⚠️ Download failed. Using fallback MACE model: {model_paths}")
    else:
        raise FileNotFoundError("❌ No MACE model found in cache, fallback, or user path.")

    return MACECalculator(model_paths=model_paths, device=device, default_dtype="float64")

def run_adsorption_optimization(output_dir="results", model_paths=None, opt_dims=None, bounds=None,
                                 nstruct=100, initpts=None, iterpts=None):
    if opt_dims is None:
        opt_dims = ["x", "y", "alpha", "beta", "gamma"]

    if bounds is None:
        bounds = {
            "x": (0, 4.07),
            "y": (0, 4.07),
            "z": (0, 5.0),
            "alpha": (0, 359),
            "beta": (0, 359),
            "gamma": (0, 359),
        }

    # Compute init/iter points if not explicitly specified
    if initpts is None or iterpts is None:
        if nstruct <= 10:
            initpts = nstruct
            iterpts = 0
        elif nstruct < 100:
            initpts = 5
            iterpts = nstruct - 5
        else:
            initpts = 20
            iterpts = nstruct - 20

    log_file = os.path.join(output_dir, "optimization_log.txt")
    initial_xyz_file = os.path.join(output_dir, "initial_configurations.xyz")
    traj_file = os.path.join(output_dir, f"{len(opt_dims)}D_optimization_trajectory.traj")
    output_graph_file = os.path.join(output_dir, "adsorption_energy_vs_steps.png")
    trajectory = Trajectory(traj_file, 'w')

    # Clear previous logs and files
    with open(log_file, 'w') as f:
        f.write("Step-by-step Optimization Log\n" + "=" * 50 + "\n")
    open(initial_xyz_file, 'w').close()

    calc = get_mace_calculator(user_model_path=model_paths)

    def func(X):
        var_dict = dict(zip(opt_dims, map(float, X.ravel())))
        x_shift = var_dict.get("x", 0.0)
        y_shift = var_dict.get("y", 0.0)
        z_shift = var_dict.get("z", 0.0)
        alpha = var_dict.get("alpha", 0.0)
        beta = var_dict.get("beta", 0.0)
        gamma = var_dict.get("gamma", 0.0)

        try:
            atoms = read(os.path.join(output_dir, "surface.inp"), format='vasp')
            atoms.set_constraint(FixAtoms(indices=[atom.index for atom in atoms]))

            mol = read(os.path.join(output_dir, "molecule.xyz"))
            center = mol.get_center_of_mass()

            if "alpha" in opt_dims: mol.rotate(alpha, 'z', center=center)
            if "beta" in opt_dims: mol.rotate(beta, 'y', center=center)
            if "gamma" in opt_dims: mol.rotate(gamma, 'x', center=center)

            min_z = min(atom.position[2] for atom in mol)
            max_z = max(atom.position[2] for atom in atoms)

            mol.translate([x_shift, y_shift, z_shift + max_z + 2.5 - min_z])
            atoms.extend(mol)

            write(initial_xyz_file, atoms, append=True)

            atoms.calc = calc
            opt = PreconLBFGS(atoms, use_armijo=True, precon=None, variable_cell=False)
            opt.run(fmax=0.01)

            energy = atoms.get_potential_energy()
            if not np.isfinite(energy):
                raise ValueError("Non-finite energy")

            step = len(results) + 1
            results.append((x_shift, y_shift, z_shift, alpha, beta, gamma, energy))
            log_step(step, energy, x_shift, y_shift, z_shift, alpha, beta, gamma, log_file)
            trajectory.write(atoms)
            return float(energy)

        except Exception as e:
            safe_parprint(f"Optimization failed at {var_dict}: {e}")
            return np.inf

    bounds_array = np.array([bounds[dim] for dim in opt_dims])
    kernel = ["rbf"] * len(opt_dims)

    print(f"Using {initpts} initial points and {iterpts} iterations for BO.")
    bo = BOMain(func, bounds_array, kernel=kernel, initpts=initpts, iterpts=iterpts, parallel_optims=16)
    res = bo.run()

    try:
        PPMain(res, pp_models=True, pp_acq_funcs=True).run()
    except Exception as e:
        safe_parprint(f"⚠️ Postprocessing failed: {e}")

    trajectory.close()

    # Combine structures
    all_structures = read(initial_xyz_file, ":") + read(traj_file, ":")
    combined_xyz = os.path.join(output_dir, "training_data_mace_opt.xyz")
    write(combined_xyz, all_structures)
    print(f"Combined structures saved to {combined_xyz}")
