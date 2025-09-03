import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_confint, proportion_effectsize
from .stats import h_to_p1


# Set uniform style for all plots
def set_plot_style():
    """Apply uniform style for plotting"""

    # Matplotlib parameters
    plt.rcParams["figure.figsize"] = [10, 6]
    plt.rcParams["font.size"] = 12
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 11
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["savefig.dpi"] = 600
    plt.rcParams["grid.alpha"] = 0.3

    # Seaborn style
    sns.set_style("whitegrid")

    # Set custom color palette
    custom_palette = ["#6B46C1", "#3182CE", "#63B3ED", "#BEE3F8", "#EBF8FF"]
    sns.set_palette(custom_palette)


set_plot_style()


# Function to plot game rounds
def plot_game_rounds(df: pd.DataFrame, lower_bound, upper_bound, log: bool = False):
    """
    Plot the distribution of game rounds by version.

    Args:
        df (pd.DataFrame): DataFrame containing the data to plot.
        lower_bound (int): Lower bound for the y-axis.
        upper_bound (int): Upper bound for the y-axis.
        log (bool): Whether to plot the log-transformed values.
    """
    if not log:  # Raw scale
        sns.boxplot(x="version", y="sum_gamerounds", data=df, hue="version", width=0.5)
        plt.title("Distribution of Game Rounds by Version")
        plt.xlabel("Game Version")
        plt.ylabel("Game Rounds")
        plt.ylim(lower_bound, upper_bound * 2)
        # plt.savefig("reports/figures/3.3_dist_of_game_rounds_by_version.png")
        plt.show()

    else:
        # Plot game rounds distributions by version
        sns.boxplot(
            x="version",
            y="log_sum_gamerounds",
            data=df,
            hue="version",
            width=0.5,
        )
        plt.title("Distribution of Game Rounds by Version (log scale)")
        plt.xlabel("Game Version")
        plt.ylabel("Game Rounds (log scale)")
        # plt.savefig("reports/figures/3.3_dist_of_game_rounds_by_version_log.png")
        plt.show()


# Function to plot assignment counts by version
def plot_assignment_counts(df: pd.DataFrame):
    """
    Plot the distribution of assignment counts by version.

    Args:
        df (pd.DataFrame): DataFrame containing the data to plot.
    """
    ax = sns.countplot(x="version", data=df, hue="version", width=0.5)
    plt.title("Assignment Counts by Version")
    plt.xlabel("Game Version")
    plt.ylabel("Number of Assignments")

    # Add value labels on top of each bar
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(
            f"{int(height)}",
            xy=(p.get_x() + p.get_width() / 2, height / 2),
            xytext=(0, 0),  # small offset
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=10,
            color="white",
            fontweight="bold",
        )

    # plt.savefig("reports/figures/4.2_assignment_counts_by_version.png")
    plt.show()


# Function to plot grouped bar with confidence intervals
def plot_retention_rates(df: pd.DataFrame):
    # Build summary for both metrics
    rows = []
    for col, label in [("retention_1", "Day-1"), ("retention_7", "Day-7")]:
        agg = (
            df.groupby("version")[col]
            .agg(["sum", "count"])
            .rename(columns={"sum": "successes", "count": "n"})
        )
        agg["rate"] = agg["successes"] / agg["n"]
        agg[["ci_low", "ci_upp"]] = agg.apply(
            lambda r: pd.Series(
                proportion_confint(int(r["successes"]), int(r["n"]), method="wilson")
            ),
            axis=1,
        )
        agg = agg.loc[["gate_30", "gate_40"]]
        for v in agg.index:
            rows.append(
                dict(
                    metric=label,
                    version=v,
                    rate=agg.loc[v, "rate"],
                    err_low=agg.loc[v, "rate"] - agg.loc[v, "ci_low"],
                    err_upp=agg.loc[v, "ci_upp"] - agg.loc[v, "rate"],
                )
            )
    out = pd.DataFrame(rows)

    colors = ["#6B46C1", "#3182CE"]  # Purple for Day-1, blue for Day-7

    fig, ax = plt.subplots()
    width = 0.35
    x = np.arange(2)  # gate_30, gate_40

    # Day-1 bars
    d1 = out[out.metric == "Day-1"].sort_values("version")
    bars1 = ax.bar(
        x - width / 2,
        d1["rate"],
        width,
        yerr=[d1["err_low"], d1["err_upp"]],
        capsize=6,
        label="Day-1",
        color=colors[0],
    )

    # Add value labels for Day-1 bars
    for bar, rate in zip(bars1, d1["rate"]):
        ax.annotate(
            f"{rate:.2%}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2),
            xytext=(0, 0),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=10,
            color="white",
            fontweight="bold",
        )

    # Day-7 bars
    d7 = out[out.metric == "Day-7"].sort_values("version")
    bars7 = ax.bar(
        x + width / 2,
        d7["rate"],
        width,
        yerr=[d7["err_low"], d7["err_upp"]],
        capsize=6,
        label="Day-7",
        color=colors[1],
    )

    # Add value labels for Day-7 bars
    for bar, rate in zip(bars7, d7["rate"]):
        ax.annotate(
            f"{rate:.2%}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2),
            xytext=(0, 0),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=10,
            color="white",
            fontweight="bold",
        )

    ax.set_xticks(x, ["gate_30", "gate_40"])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_ylabel("Retention Rate")
    ax.set_title("Retention Rates by Version with 95% CI")
    ax.legend()

    plt.tight_layout()
    # plt.savefig("reports/figures/4.3_retention_rates_by_version_95_ci.png")
    plt.show()


# Function to plot histogram of player count - game rounds distribution
def plot_game_rounds_dist(df: pd.DataFrame, log: bool = False):
    if not log:  # Raw scale
        # Plot histogram for control group (gate_30)
        sns.histplot(
            data=df[df["version"] == "gate_30"],
            x="sum_gamerounds",
            bins=50,
            alpha=0.7,
            label="Control (gate_30)",
        )

        # Plot histogram for treatment group (gate_40)
        sns.histplot(
            data=df[df["version"] == "gate_40"],
            x="sum_gamerounds",
            bins=50,
            alpha=0.7,
            label="Treatment (gate_40)",
        )

        plt.title("Player Count - Game Rounds Distribution (raw scale)")
        plt.xlabel("Game Rounds")
        plt.ylabel("Player Count")
        plt.legend()
        # plt.savefig("reports/figures/4.4_player_count_game_rounds_dist.png")
        plt.show()

    else:  # Log scale
        # Plot histogram for control group (gate_30)
        sns.histplot(
            data=df[df["version"] == "gate_30"],
            x="log_sum_gamerounds",
            bins=50,
            alpha=0.7,
            label="Control (gate_30)",
        )

        # Plot histogram for treatment group (gate_40)
        sns.histplot(
            data=df[df["version"] == "gate_40"],
            x="log_sum_gamerounds",
            bins=50,
            alpha=0.7,
            label="Treatment (gate_40)",
        )

        plt.title("Player Count - Game Rounds Distribution (log scale)")
        plt.xlabel("Game Rounds (log scale)")
        plt.ylabel("Player Count (log scale)")
        plt.legend()
        # plt.savefig("reports/figures/4.4_player_count_game_rounds_dist_log.png")
        plt.show()


def prepare_axes_power_vs_mde(p0, nob, alpha):
    mde_points = np.linspace(0, 2.5, 51)
    powers = []
    for pp in mde_points:
        p1 = min(max(p0 + pp / 100.0, 1e-9), 1 - 1e-9)
        effectsize = proportion_effectsize(p1, p0)
        power_analysis = NormalIndPower()
        pw = power_analysis.solve_power(
            effect_size=effectsize,
            nobs1=nob,
            alpha=alpha,
            ratio=1.0,
            alternative="two-sided",
        )
        powers.append(pw)

    return mde_points, powers


# Function to plot power vs. MDE
def plot_power_vs_mde(p0, nob, mde_pp_current, alpha):
    axes = prepare_axes_power_vs_mde(p0, nob, alpha)

    plt.plot(axes[0], axes[1], color="#6B46C1", linewidth=2)
    plt.axhline(0.8, linestyle="--", linewidth=1, color="#63B3ED")

    # Add point for current MDE
    plt.scatter([mde_pp_current], [0.80], color="#3182CE", zorder=5)
    plt.text(
        mde_pp_current + 0.3,
        0.72,
        f"Current MDE = {mde_pp_current:.2f} pp",
        ha="center",
        color="#3182CE",
    )

    # Format y-axis as percentages
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    plt.xlabel("Minimum Detectable Effect (percentage point)")
    plt.ylabel("Power at current N")
    plt.title("Power vs. MDE at Current Sample Size")
    plt.tight_layout()
    # plt.savefig("reports/figures/5_power_vs_mde_at_current_n.png")
    plt.show()


def prepare_axes_mde_vs_sample(p0, alpha, power):
    # Plot — MDE vs n per group (balanced @ 80% power)
    n_values = np.linspace(5_000, 150_000, 60)  # per-group sizes for planning
    pp = []
    for n in n_values:
        power_analysis = NormalIndPower()
        effectsize_required = power_analysis.solve_power(
            effect_size=None,
            nobs1=n,
            alpha=alpha,
            power=power,
            ratio=1.0,
            alternative="two-sided",
        )
        p1_required = h_to_p1(
            effectsize_required, p0
        )  # invert h to get p1, then convert to pp uplift
        pp.append((p1_required - p0) * 100)

    return n_values, pp


# Function to plot MDE vs. Sample Size
def plot_mde_vs_sample(p0, alpha, power, n, mde_pp_current):
    axes = prepare_axes_mde_vs_sample(p0, alpha, power)

    plt.plot(axes[0], axes[1], color="#6B46C1", linewidth=2)
    plt.scatter([n], [mde_pp_current], color="#3182CE", zorder=5)
    plt.text(
        n + 25000,
        mde_pp_current + 0.1,
        f"Current N = {n}, MDE = {mde_pp_current:.2f} pp",
        ha="center",
        color="#3182CE",
    )

    plt.xlabel("N per Group")
    plt.ylabel("MDE (percentage points)")
    plt.title("MDE vs. Sample Size per Group at 80% Power")
    plt.tight_layout()
    # plt.savefig("reports/figures/5_mde_vs_n_per_group_at_80_power.png")
    plt.show()
