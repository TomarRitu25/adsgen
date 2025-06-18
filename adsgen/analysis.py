import argparse
import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import csv
from ase.io import read


def load_energy_list_from_txt(file_path):
    with open(file_path) as f:
        return sorted([float(line.strip()) for line in f if line.strip()])


def save_energy_list_to_txt(energies, path):
    with open(path, 'w') as f:
        for e in energies:
            f.write(f"{e:.6f}\n")
    print(f"💾 Saved energies to {path}")


def load_energies_from_traj(traj_path):
    frames = read(traj_path, index=":")
    return sorted([float(atoms.get_potential_energy()) for atoms in frames])


def extract_dft_energies_from_outcars(base_dir="vasp_inputs"):
    """Parse total energies from OUTCAR or OSZICAR in each conf_* subfolder."""
    energies = []
    conf_dirs = sorted(glob.glob(os.path.join(base_dir, "conf_*")))

    for d in conf_dirs:
        outcar = os.path.join(d, "OUTCAR")
        oszicar = os.path.join(d, "OSZICAR")

        energy = None
        if os.path.exists(outcar):
            with open(outcar) as f:
                for line in reversed(f.readlines()):
                    if "free  energy   TOTEN" in line:
                        energy = float(line.split()[-2])
                        break
        elif os.path.exists(oszicar):
            with open(oszicar) as f:
                for line in reversed(f.readlines()):
                    if "E0=" in line:
                        energy = float(line.split("E0=")[-1].split()[0])
                        break

        if energy is not None:
            energies.append(energy)
        else:
            print(f"⚠️  Warning: No energy found in {d}")

    return sorted(energies)


def compare_energies(mace_energies, dft_energies, out_file):
    if len(mace_energies) != len(dft_energies):
        print(f"⚠️  Warning: Length mismatch – MACE={len(mace_energies)} vs DFT={len(dft_energies)}")
        min_len = min(len(mace_energies), len(dft_energies))
        mace_energies = mace_energies[:min_len]
        dft_energies = dft_energies[:min_len]

    # Compute metrics
    diffs = np.array(mace_energies) - np.array(dft_energies)
    rmse = np.sqrt(np.mean(diffs ** 2))
    mae = np.mean(np.abs(diffs))

    print(f"\n📊 Energy Comparison Metrics:")
    print(f"  RMSE: {rmse:.4f} eV")
    print(f"  MAE:  {mae:.4f} eV")

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(mace_energies, label="MACE", marker='o')
    plt.plot(dft_energies, label="DFT", marker='x')
    plt.xlabel("Configuration (sorted)")
    plt.ylabel("Adsorption Energy (eV)")
    plt.title(f"MACE vs DFT Adsorption Energies\nRMSE={rmse:.3f} eV, MAE={mae:.3f} eV")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_file)
    print(f"✅ Saved plot to {out_file}")

    # Save CSV side-by-side
    csv_path = out_file.replace(".png", ".csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "MACE_energy", "DFT_energy", "difference"])
        for i, (m, d) in enumerate(zip(mace_energies, dft_energies)):
            writer.writerow([i, f"{m:.6f}", f"{d:.6f}", f"{m - d:.6f}"])
    print(f"📄 Saved comparison CSV to {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Compare MACE and DFT adsorption energies")
    parser.add_argument("--traj", type=str, help="Trajectory file (.traj) to extract MACE energies")
    parser.add_argument("--mace", type=str, help="Text file with MACE energies (one per line)")
    parser.add_argument("--dft", type=str, help="Text file with DFT energies (one per line)")
    parser.add_argument("--dft-dir", type=str, help="Directory containing VASP OUTCAR/OSZICAR files")
    parser.add_argument("--out", type=str, required=True, help="Path to save the output plot")
    parser.add_argument("--save-mace", type=str, default="mace_extracted_energies.txt", help="File to save extracted MACE energies")
    parser.add_argument("--save-dft", type=str, default="dft_extracted_energies.txt", help="File to save extracted DFT energies")

    args = parser.parse_args()

    # Load MACE energies
    if args.traj:
        mace_energies = load_energies_from_traj(args.traj)
        save_energy_list_to_txt(mace_energies, args.save_mace)
    elif args.mace:
        mace_energies = load_energy_list_from_txt(args.mace)
    else:
        raise ValueError("You must provide either --traj or --mace")

    # Load DFT energies
    if args.dft:
        dft_energies = load_energy_list_from_txt(args.dft)
    elif args.dft_dir:
        dft_energies = extract_dft_energies_from_outcars(args.dft_dir)
        save_energy_list_to_txt(dft_energies, args.save_dft)
    else:
        raise ValueError("You must provide either --dft or --dft-dir")

    compare_energies(mace_energies, dft_energies, args.out)


if __name__ == "__main__":
    main()

