import pandas as pd


def build_results_table(
    ret1_results,
    ret7_results,
    rounds_results,
    bootstrap_result,
    guardrail_adj,
    engagement_stats,
    alpha,
):
    rows = []
    # Day-7 retention
    rows.append(
        {
            "Metric": "Day-7 retention",
            "Control (gate_30)": f"{ret7_results[0]:.2%} (95% CI [{ret7_results[1]:.2%}, {ret7_results[2]:.2%}])",
            "Treatment (gate_40)": f"{ret7_results[3]:.2%} (95% CI [{ret7_results[4]:.2%}, {ret7_results[5]:.2%}])",
            "Absolute Δ (pp/unit)": f"{ret7_results[8]:.2f} pp (95% CI [{ret7_results[9] * 100:.2f}, {ret7_results[10] * 100:.2f}])",
            "Relative Δ (%)": f"{ret7_results[11]:.2f}%",
            "Effect size": f"Cohen's h = {ret7_results[12]:.2f}",
            "Statistic": f"z = {ret7_results[6]:.2f}",
            "p-value": f"{ret7_results[7]:.4f}",
            "Adjusted p-value": None,
            "Significant?": "Yes" if ret7_results[7] < alpha else "No",
        }
    )
    # Day-1 retention
    rows.append(
        {
            "Metric": "Day-1 retention",
            "Control (gate_30)": f"{ret1_results[0]:.2%} (95% CI [{ret1_results[1]:.2%}, {ret1_results[2]:.2%}])",
            "Treatment (gate_40)": f"{ret1_results[3]:.2%} (95% CI [{ret1_results[4]:.2%}, {ret1_results[5]:.2%}])",
            "Absolute Δ (pp/unit)": f"{ret1_results[8]:.2f} pp (95% CI [{ret1_results[9] * 100:.2f}, {ret1_results[10] * 100:.2f}])",
            "Relative Δ (%)": f"{ret1_results[11]:.2f}%",
            "Effect size": f"Cohen's h = {ret1_results[12]:.2f}",
            "Statistic": f"z = {ret1_results[6]:.2f}",
            "p-value": f"{ret1_results[7]:.4f}",
            "Adjusted p-value": f"{guardrail_adj[1][0]:.6f}",
            "Significant?": "Yes" if guardrail_adj[1][0] < alpha else "No",
        }
    )
    # Mann-Whitney U for game rounds
    rows.append(
        {
            "Metric": "Mann-Whitney U test on game rounds",
            "Control (gate_30)": f"{engagement_stats[2]:.2f} (median: {engagement_stats[3]:.2f})",
            "Treatment (gate_40)": f"{engagement_stats[4]:.2f} (median: {engagement_stats[5]:.2f})",
            "Absolute Δ (pp/unit)": f"{engagement_stats[6]:.2f}",
            "Relative Δ (%)": None,
            "Effect size": None,
            "Statistic": f"U = {rounds_results[0]:.0f}",
            "p-value": f"{rounds_results[1]:.4f}",
            "Adjusted p-value": f"{guardrail_adj[1][1]:.6f}",
            "Significant?": "Yes" if guardrail_adj[1][1] < alpha else "No",
        }
    )
    # Welch's t-test on log-transformed game rounds
    rows.append(
        {
            "Metric": "Welch's t-test on log-transformed game rounds",
            "Control (gate_30)": f"{engagement_stats[7].mean():.6f}",
            "Treatment (gate_40)": f"{engagement_stats[8].mean():.6f}",
            "Absolute Δ (pp/unit)": None,
            "Relative Δ (%)": None,
            "Effect size": None,
            "Statistic": f"t = {rounds_results[2]:.2f}",
            "p-value": f"{rounds_results[3]:.4f}",
            "Adjusted p-value": f"{guardrail_adj[1][2]:.6f}",
            "Significant?": "Yes" if guardrail_adj[1][2] < alpha else "No",
        }
    )
    # Bootstrap for mean difference in game rounds
    rows.append(
        {
            "Metric": "Bootstrap delta mean rounds",
            "Control (gate_30)": f"{engagement_stats[0].mean():.2f}",
            "Treatment (gate_40)": f"{engagement_stats[1].mean():.2f}",
            "Absolute Δ (pp/unit)": f"{bootstrap_result[0]:.2f}",
            "Relative Δ (%)": None,
            "Effect size": None,
            "Statistic": f"95% CI for mean difference: [{bootstrap_result[1]:.2f}, {bootstrap_result[2]:.2f}]",
            "p-value": None,
            "Adjusted p-value": None,
            "Significant?": None,
        }
    )

    return pd.DataFrame(rows)
