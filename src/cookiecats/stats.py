# Imports
import math
import numpy as np
import pandas as pd
from scipy.stats import chisquare, mannwhitneyu, ttest_ind
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import (
    confint_proportions_2indep,
    proportion_confint,
    proportion_effectsize,
    proportions_ztest,
)


# Function to test SRM
def test_srm_chi2(df: pd.DataFrame, control_players: int, treatment_players: int):
    # Calculate total players
    total_players = control_players + treatment_players

    # Create lists of observed and expected counts per version
    observed = [control_players, treatment_players]
    expected = [total_players / 2, total_players / 2]

    # Create allocation ratios per version
    control_perc = control_players / total_players
    treatment_perc = treatment_players / total_players

    # Run chi-square test for SRM
    chi_stat, srm_chi2_pval = chisquare(f_obs=observed, f_exp=expected)

    return srm_chi2_pval, control_perc, treatment_perc


# Invert Cohen's h to get p1 given p0 and h
def h_to_p1(h, p0):
    return np.sin(np.arcsin(np.sqrt(p0)) + h / 2.0) ** 2


def solve_mde(df: pd.DataFrame, alpha: float, power: float, p0: float):
    # Solve for the effect size h required to achieve 80% power at the actual N
    N = df[df["version"] == "gate_30"].shape[0]  # actual sample size

    power_analysis = NormalIndPower()
    effectsize_needed = power_analysis.solve_power(
        effect_size=None,
        nobs1=N,
        alpha=alpha,
        power=power,
        ratio=1.0,
        alternative="two-sided",
    )

    # Convert h back to absolute uplift in percentage points
    p1_mde = h_to_p1(effectsize_needed, p0)
    mde_pp_current = (p1_mde - p0) * 100

    return N, mde_pp_current


def solve_required_n(alpha: float, power: float, p0: float):
    # Choose target MDEs in percentage points (pp)
    targets_pp = [0.5, 0.8, 1.0, 1.5, 2.0]

    rows = []
    for pp in targets_pp:
        # Calculate the required sample size for each target MDE
        p1_target = min(max(p0 + pp / 100.0, 1e-9), 1 - 1e-9)
        effectsize_target = proportion_effectsize(p1_target, p0)
        power_analysis = NormalIndPower()
        n_per_group = power_analysis.solve_power(
            effect_size=effectsize_target,
            nobs1=None,
            alpha=alpha,
            power=power,
            ratio=1.0,
            alternative="two-sided",
        )

        rows.append(
            {"Target MDE (pp)": pp, "Required N per group": int(math.ceil(n_per_group))}
        )

    return pd.DataFrame(rows)
