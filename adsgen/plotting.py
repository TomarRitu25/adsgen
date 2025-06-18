import matplotlib.pyplot as plt

def plot_energy_from_rst(rst_path, save_path="boss_energy_vs_step.png"):
    """
    Parses boss.rst file and plots energy vs step with global minimum marked.
    """
    step = []
    energy = []

    with open(rst_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                parts = line.split()
                try:
                    step.append(int(parts[0]))
                    energy.append(float(parts[-1]))
                except (ValueError, IndexError):
                    continue

    if not step or not energy:
        print("⚠️ No data found in boss.rst for plotting.")
        return

    min_idx = energy.index(min(energy))

    plt.figure(figsize=(8, 5))
    plt.plot(step, energy, marker='o', label='Energy')
    plt.scatter([step[min_idx]], [energy[min_idx]], color='red', label='Global Min')
    plt.xlabel('Step')
    plt.ylabel('Energy (eV)')
    plt.title('BOSS Energy vs. Step')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

    print(f"📈 Energy plot saved to {save_path}")

