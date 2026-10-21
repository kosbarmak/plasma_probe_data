import pandas as pd
import matplotlib.pyplot as plt

# 1) Read raw IV readings
df = pd.read_excel(
    "data.xlsx",
    sheet_name="RPA",
    skiprows=4,
    header=None,
    usecols="A:D",
    names=["V1", "A1", "V2", "A2"],
)

df = df.apply(pd.to_numeric, errors="coerce")

df = df.dropna(how="all")


def plot_rpa(df, voltage_column, current_column, operating_voltage):
    # ========================================== 
    # 2) Smooth out data
    # Theres a sweep every 400 rows
    sweeps = []
    for start in range(0, len(df), 401):
        sweeps.append(df.iloc[start : start + 401].copy())
    selected_indices = range(0, len(sweeps), 2)


    # ========================================== 
    # 3) Differentiate to obtain energy distribution
    smoothed_currents = []
    energy_distributions = []
    for i, sweep in enumerate(sweeps):
        # A_smoothed = sweep[current_column].rolling(
        #     window=21, center=True, min_periods=1
        # ).mean()

        A_smoothed = sweep[current_column].rolling(
            window=11, center=True
        ).mean()

        V = sweep[voltage_column]
        dI = A_smoothed.diff()
        dV = V.diff()
        distribution = -dI / dV

        smoothed_currents.append(A_smoothed)
        energy_distributions.append(distribution)

    energy_peak = max(energy_distributions[i].max() for i in selected_indices)
    normalized_energy_distributions = [
        distribution / energy_peak
        for distribution in energy_distributions
    ]


    # ==========================================
    # 4) Convert to axial velocity distribution
    e = 1.602176634e-19       # Elementary charge, C
    m_xe = 131.293 * 1.66053906660e-27  # Xenon ion mass, kg

    velocities = []
    velocity_distributions = []
    for i, sweep in enumerate(sweeps):
        V = sweep[voltage_column]
        distribution = energy_distributions[i]
        # Assume singly charged xenon and no plasma-potential correction.
        # Negative energies are excluded from the conversion.
        energy_eV = V.where(V >= 0)
        velocity = (2 * e * energy_eV / m_xe) ** 0.5  # m/s

        # Transform the distribution, not just its horizontal axis.
        velocity_distribution = distribution * m_xe * velocity / e
        velocities.append(velocity)
        velocity_distributions.append(velocity_distribution)

    velocity_peak = max(velocity_distributions[i].max() for i in selected_indices)
    normalized_velocity_distributions = [
        distribution / velocity_peak
        for distribution in velocity_distributions
    ]


    # ========================================== 
    # Display the results
    fig = plt.figure(figsize=(24, 10), layout="constrained")
    fig.suptitle(f"RPA — {operating_voltage} V", fontweight="bold")
    raw_row, distribution_rows, velocity_row = fig.subfigures(
        3, 1, height_ratios=[1, 2, 1]
    )
    distribution_rows.suptitle(f"RPA — {operating_voltage} V", fontweight="bold")
    smoothed_row, energy_row = distribution_rows.subfigures(2, 1)
    rows = [raw_row, smoothed_row, energy_row, velocity_row]

    titles = [
        "Raw current",
        "Smoothed current",
        "Normalized energy distribution",
        f"RPA — {operating_voltage} V — Normalized axial velocity distribution",
    ]
    axes = []

    for row, title in zip(rows, titles):
        row.suptitle(title, fontweight="bold")
        axes.append(row.subplots(1, len(selected_indices), sharex=True, sharey=True))

    for column, i in enumerate(selected_indices):
        V = sweeps[i][voltage_column]
        axes[0][column].plot(V, sweeps[i][current_column])
        axes[0][column].set_title(f"Sweep #{i + 1}", fontweight="bold")
        axes[1][column].plot(V, smoothed_currents[i])
        axes[1][column].set_title(f"Sweep #{i + 1}", fontweight="bold")
        # For singly charged ions, retarding voltage in V maps numerically to energy in eV.
        axes[2][column].plot(V, normalized_energy_distributions[i])
        axes[3][column].plot(
            velocities[i] / 1000, normalized_velocity_distributions[i]
        )
        axes[3][column].set_title(f"Sweep #{i + 1}", fontweight="bold")

    rows[0].supxlabel("RPA voltage (V)")
    rows[1].supxlabel("RPA voltage (V)")
    rows[2].supxlabel("Ion energy (eV)")
    rows[3].supxlabel("Axial ion velocity (km/s)")

    axes[0][0].set_ylabel("RPA current (A)")
    axes[1][0].set_ylabel("RPA current (A)")
    axes[2][0].set_ylabel("Normalized −dI/dV")
    axes[3][0].set_ylabel("Normalized velocity distribution")


plot_rpa(df, "V1", "A1", 300)
plot_rpa(df, "V2", "A2", 150)
plt.show()
