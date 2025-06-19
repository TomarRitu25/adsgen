import os
import argparse
from pathlib import Path
from adsgen.surface import run_adsorption_optimization
from adsgen.vasp_single_step_opt import run_single_step_optimization


def run_generation(
    mol_path,
    surf_path,
    output_dir="results",
    skip_vasp=False,
    vasp_command="mpirun -np 4 vasp_std",
    nstruct=100,
    initpts=None,
    iterpts=None,
    opt_dims=None,
    bounds_dict=None,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    mol_dst = output_dir / "molecule.xyz"
    surf_dst = output_dir / "surface.inp"

    if Path(mol_path).resolve() != mol_dst.resolve():
        os.system(f"cp {mol_path} {mol_dst}")
        print(f"Copied molecule: {mol_path} → {mol_dst}")
    else:
        print(f"⚠️ Source and destination are the same: {mol_path}")

    if Path(surf_path).resolve() != surf_dst.resolve():
        os.system(f"cp {surf_path} {surf_dst}")
        print(f"Copied surface: {surf_path} → {surf_dst}")
    else:
        print(f"⚠️ Source and destination are the same: {surf_path}")

    print("Running BOSS + MACE training structure generation...")

    run_adsorption_optimization(
        output_dir=str(output_dir),
        model_paths=None,
        opt_dims=opt_dims,
        bounds=bounds_dict,
        nstruct=nstruct,
        initpts=initpts,
        iterpts=iterpts,
    )

    run_single_step_optimization(skip_vasp=skip_vasp, vasp_command=vasp_command)


def main():
    parser = argparse.ArgumentParser(
        description="Generate training structures using BOSS + MACE with optional VASP single-step optimization."
    )
    parser.add_argument("--mol", type=str, required=True, help="Path to molecule.xyz")
    parser.add_argument("--surf", type=str, required=True, help="Path to surface.inp")
    parser.add_argument("--out", type=str, default="results", help="Output directory")
    parser.add_argument("--skip-vasp", action="store_true", help="Skip VASP optimization")
    parser.add_argument("--vasp_command", type=str, default="mpirun -np 4 vasp_std", help="VASP command")

    parser.add_argument("--nstruct", type=int, default=100, help="Total number of structures to generate")
    parser.add_argument("--initpts", type=int, help="Number of initial points (overrides default logic)")
    parser.add_argument("--iterpts", type=int, help="Number of BO iterations (overrides default logic)")

    parser.add_argument(
        "--opt-dims",
        nargs="+",
        choices=["x", "y", "z", "alpha", "beta", "gamma"],
        default=["x", "y", "alpha", "beta", "gamma"],
        help="Degrees of freedom to optimize (translation/rotation)"
    )
    parser.add_argument("--bounds-x", nargs=2, type=float, help="Bounds for x shift")
    parser.add_argument("--bounds-y", nargs=2, type=float, help="Bounds for y shift")
    parser.add_argument("--bounds-z", nargs=2, type=float, help="Bounds for z shift")
    parser.add_argument("--bounds-alpha", nargs=2, type=float, help="Bounds for alpha rotation")
    parser.add_argument("--bounds-beta", nargs=2, type=float, help="Bounds for beta rotation")
    parser.add_argument("--bounds-gamma", nargs=2, type=float, help="Bounds for gamma rotation")

    args = parser.parse_args()

    # Parse bounds
    bounds_dict = {}
    for dim in ["x", "y", "z", "alpha", "beta", "gamma"]:
        val = getattr(args, f"bounds_{dim}")
        if val:
            bounds_dict[dim] = tuple(val)

    run_generation(
        mol_path=args.mol,
        surf_path=args.surf,
        output_dir=args.out,
        skip_vasp=args.skip_vasp,
        vasp_command=args.vasp_command,
        nstruct=args.nstruct,
        initpts=args.initpts,
        iterpts=args.iterpts,
        opt_dims=args.opt_dims,
        bounds_dict=bounds_dict,
    )


if __name__ == "__main__":
    main()
