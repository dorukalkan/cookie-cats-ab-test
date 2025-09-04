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
def test_srm_chi2(control_players: int, treatment_players: int):
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


def test_two_prop_z(df, ctrl, treat, col, alpha, p0):
    # Successes = players retained at day-7
    success_ctrl = df[df["version"] == "gate_30"][col].sum()
    success_treat = df[df["version"] == "gate_40"][col].sum()

    successes = [success_ctrl, success_treat]
    nobs = [ctrl, treat]

    # Two-proportion z-test
    z_stat, pval = proportions_ztest(successes, nobs, alternative="two-sided")

    # Confidence intervals for each group
    (ci_ctrl_low, ci_ctrl_high) = proportion_confint(
        success_ctrl, ctrl, alpha=alpha, method="wilson"
    )
    (ci_treat_low, ci_treat_high) = proportion_confint(
        success_treat, treat, alpha=alpha, method="wilson"
    )

    # Calculate observed proportions and difference
    prop_ctrl = success_ctrl / ctrl
    prop_treat = success_treat / treat
    delta = prop_treat - prop_ctrl
    delta_abs_pp = delta * 100

    # Confidence intervals for the difference
    (ci_delta_low, ci_delta_high) = confint_proportions_2indep(
        success_treat,
        treat,
        success_ctrl,
        ctrl,
        method="score",
    )

    # Calculate relative change
    delta_rel_pct = (prop_treat / prop_ctrl - 1) * 100

    # Cohen's h
    p1 = df[df["version"] == "gate_40"][col].mean()
    h = proportion_effectsize(p0, p1)

    return (
        prop_ctrl,
        ci_ctrl_low,
        ci_ctrl_high,
        prop_treat,
        ci_treat_low,
        ci_treat_high,
        z_stat,
        pval,
        delta_abs_pp,
        ci_delta_low,
        ci_delta_high,
        delta_rel_pct,
        h,
    )


def calculate_engagement_stats(df):
    # Game rounds played per version
    rounds_ctrl = df[df["version"] == "gate_30"]["sum_gamerounds"]
    rounds_treat = df[df["version"] == "gate_40"]["sum_gamerounds"]

    # Engagement statistics for context
    mean_ctrl = rounds_ctrl.mean()
    median_ctrl = rounds_ctrl.median()
    mean_treat = rounds_treat.mean()
    median_treat = rounds_treat.median()
    delta_mean = mean_treat - mean_ctrl

    # Transform game rounds
    log_ctrl = np.log1p(rounds_ctrl)
    log_treat = np.log1p(rounds_treat)

    return (
        rounds_ctrl,  # 0
        rounds_treat,  # 1
        mean_ctrl,  # 2
        median_ctrl,  # 3
        mean_treat,  # 4
        median_treat,  # 5
        delta_mean,  # 6
        log_ctrl,  # 7
        log_treat,  # 8
    )


def test_game_rounds(engagement_stats):
    # Mann-Whitney U test
    u_stat, pval_rounds = mannwhitneyu(
        engagement_stats[0], engagement_stats[1], alternative="two-sided"
    )

    # Welch's t-test (unequal variances)
    tstat_log, pval_log = ttest_ind(
        engagement_stats[7],
        engagement_stats[8],
        equal_var=False,
        alternative="two-sided",
    )

    return u_stat, pval_rounds, tstat_log, pval_log


def bootstrap_mean_diff(rounds_ctrl, rounds_treat):
    # Simple percentile bootstrap for the mean difference on the raw scale
    np.random.seed(42)
    B = 5000
    boot_diffs = []

    for i in range(B):
        # Resample with replacement from both groups
        ctrl_sample_mean = rounds_ctrl.sample(n=len(rounds_ctrl), replace=True).mean()
        treat_sample_mean = rounds_treat.sample(
            n=len(rounds_treat), replace=True
        ).mean()
        boot_diffs.append(ctrl_sample_mean - treat_sample_mean)

    boot_diffs = np.array(boot_diffs)
    ci_low, ci_high = np.percentile(boot_diffs, [2.5, 97.5])
    obs_diff = rounds_treat.mean() - rounds_ctrl.mean()

    return obs_diff, ci_low, ci_high
