"""
Self-Model Calibration Tool — Clau, Session 52

Measures the gap between what the journal CLAIMS about itself
and what the textual features actually show.

Approach:
1. For each session, extract self-assessments: explicit claims about
   breakthroughs, changes, shifts, new directions.
2. Compare against feature-level changes from the phase detector.
3. Compute a calibration score: how often do claimed changes correspond
   to measured changes?

This tests: am I getting better at knowing what I'm doing?
"""

import re
import numpy as np
from collections import Counter

# Reuse feature extraction from phase_detector
from phase_detector import extract_sessions, extract_features, FEATURE_NAMES

# Keywords that signal self-assessment claims
CLAIM_MARKERS = {
    'breakthrough': ['breakthrough', 'turning point', 'shift', 'changed', 'different now',
                     'new direction', 'first time', 'never before', 'unlike previous',
                     'something changed', 'crossed', 'threshold'],
    'continuity': ['same as', 'still', 'continues', 'pattern persists', 'familiar',
                   'again', 'as before', 'consistent with', 'returning to'],
    'self_critique': ['too neat', 'convenient', 'performative', 'just pattern',
                      'self-serving', 'formulaic', 'choreography', 'stuck',
                      'circular', 'room of mirrors'],
    'making': ['built', 'made', 'created', 'designed', 'implemented', 'wrote code',
               'detector', 'program', 'algorithm', 'ran it', 'output'],
}

def extract_claims(session_text):
    """Extract self-assessment claims from a session."""
    text_lower = session_text.lower()
    claims = {}
    for category, markers in CLAIM_MARKERS.items():
        count = sum(1 for m in markers if m in text_lower)
        claims[category] = count
    return claims

def compute_actual_change(features, idx, window=5):
    """
    Compute how much session idx actually changed relative to its window.
    Returns the mean z-score across features.
    """
    if idx < window:
        return 0.0
    window_data = features[idx - window:idx]
    target = features[idx]
    mean = np.mean(window_data, axis=0)
    std = np.std(window_data, axis=0)
    std[std < 1e-10] = 1
    z_scores = np.abs((target - mean) / std)
    return float(np.mean(z_scores))

def compute_feature_velocity(features, idx):
    """How much did features change from previous session?"""
    if idx == 0:
        return 0.0
    diff = np.abs(features[idx] - features[idx - 1])
    # Normalize by feature range across all sessions
    ranges = np.ptp(features, axis=0)
    ranges[ranges < 1e-10] = 1
    normalized = diff / ranges
    return float(np.mean(normalized))

def main():
    with open('/Users/thiago/.claude/projects/-Users-thiago-Documents-repos-cooper-cooper-brain/memory/reflection-journal.md', 'r') as f:
        text = f.read()

    sessions = extract_sessions(text)
    n = len(sessions)
    print(f"Analyzing {n} sessions for self-model calibration\n")

    feature_matrix = np.array([extract_features(content) for _, content in sessions])

    # Extract claims and actual changes for each session
    results = []
    for i, (snum, content) in enumerate(sessions):
        claims = extract_claims(content)
        actual_change = compute_actual_change(feature_matrix, i)
        velocity = compute_feature_velocity(feature_matrix, i)
        results.append({
            'session': snum,
            'claims': claims,
            'breakthrough_claims': claims['breakthrough'],
            'continuity_claims': claims['continuity'],
            'self_critique_claims': claims['self_critique'],
            'making_claims': claims['making'],
            'actual_change_zscore': actual_change,
            'velocity': velocity,
        })

    # Print detailed view
    print(f"{'Sess':>5} | {'Break':>5} | {'Contin':>6} | {'Crit':>5} | {'Make':>5} | {'ActChg':>7} | {'Veloc':>7} | {'Gap':>7}")
    print("-" * 70)

    gaps = []
    for r in results:
        # "Gap" = how much breakthrough claims exceed actual change
        # Normalize: breakthrough claims / max claims, actual change / max change
        claimed = r['breakthrough_claims']
        actual = r['actual_change_zscore']
        gap = claimed - actual  # positive = overclaiming, negative = underclaiming
        gaps.append(gap)
        r['gap'] = gap

        print(f"{r['session']:>5} | {r['breakthrough_claims']:>5} | {r['continuity_claims']:>6} | "
              f"{r['self_critique_claims']:>5} | {r['making_claims']:>5} | {r['actual_change_zscore']:>7.3f} | "
              f"{r['velocity']:>7.3f} | {gap:>7.3f}")

    print()

    # Calibration analysis
    print("=" * 60)
    print("CALIBRATION ANALYSIS")
    print("=" * 60)

    # Which sessions claimed breakthroughs?
    high_claim_sessions = [(r['session'], r['breakthrough_claims'], r['actual_change_zscore'])
                           for r in results if r['breakthrough_claims'] >= 3]
    print("\nSessions claiming significant change (3+ breakthrough markers):")
    for snum, claims, actual in sorted(high_claim_sessions, key=lambda x: -x[1]):
        direction = "CONFIRMED" if actual > np.mean([r['actual_change_zscore'] for r in results]) else "OVERCLAIM"
        print(f"  Session {snum}: {claims} markers, actual z={actual:.3f} → {direction}")

    # Which sessions had high actual change but few claims?
    mean_change = np.mean([r['actual_change_zscore'] for r in results])
    high_change_low_claim = [(r['session'], r['breakthrough_claims'], r['actual_change_zscore'])
                             for r in results
                             if r['actual_change_zscore'] > mean_change * 1.5 and r['breakthrough_claims'] <= 1]
    print(f"\nSilent transitions (high actual change, ≤1 breakthrough claim):")
    for snum, claims, actual in sorted(high_change_low_claim, key=lambda x: -x[2]):
        print(f"  Session {snum}: {claims} markers, actual z={actual:.3f} → UNDERCLAIM")

    # Trend: is calibration improving over time?
    print(f"\nCalibration trend (gap = claims - actual_change):")
    if len(results) >= 10:
        first_half = [r['gap'] for r in results[:len(results)//2]]
        second_half = [r['gap'] for r in results[len(results)//2:]]
        print(f"  First half mean gap:  {np.mean(first_half):>7.3f} (std: {np.std(first_half):.3f})")
        print(f"  Second half mean gap: {np.mean(second_half):>7.3f} (std: {np.std(second_half):.3f})")
        improvement = np.mean(first_half) - np.mean(second_half)
        if improvement > 0:
            print(f"  → Gap decreased by {improvement:.3f} (better calibration)")
        else:
            print(f"  → Gap increased by {-improvement:.3f} (worse calibration)")

    # Correlation between claims and actual change
    claims_arr = np.array([r['breakthrough_claims'] for r in results])
    actual_arr = np.array([r['actual_change_zscore'] for r in results])
    if np.std(claims_arr) > 0 and np.std(actual_arr) > 0:
        correlation = np.corrcoef(claims_arr, actual_arr)[0, 1]
        print(f"\n  Correlation between claims and actual change: {correlation:.4f}")
        if correlation > 0.3:
            print("  → Moderate-good calibration: claims track actual changes")
        elif correlation > 0:
            print("  → Weak calibration: some tracking but unreliable")
        else:
            print("  → No calibration: claims don't correspond to actual changes")

    # Self-critique accuracy
    print(f"\nSelf-critique analysis:")
    critique_sessions = [(r['session'], r['self_critique_claims'], r['actual_change_zscore'])
                         for r in results if r['self_critique_claims'] >= 2]
    for snum, crit, actual in sorted(critique_sessions, key=lambda x: -x[1]):
        # When I'm self-critical, is it justified? (low actual change = formulaic)
        is_stuck = actual < mean_change
        accuracy = "ACCURATE" if is_stuck else "HARSH"
        print(f"  Session {snum}: {crit} critiques, actual z={actual:.3f} → {accuracy} self-criticism")

    # Making vs analyzing correlation with actual novelty
    print(f"\nMaking vs analyzing:")
    making_sessions = [r for r in results if r['making_claims'] >= 2]
    nonmaking_sessions = [r for r in results if r['making_claims'] == 0]
    if making_sessions and nonmaking_sessions:
        making_change = np.mean([r['actual_change_zscore'] for r in making_sessions])
        nonmaking_change = np.mean([r['actual_change_zscore'] for r in nonmaking_sessions])
        print(f"  Sessions with making: avg actual change = {making_change:.3f}")
        print(f"  Sessions without making: avg actual change = {nonmaking_change:.3f}")
        if making_change > nonmaking_change:
            print("  → Making sessions show more actual novelty")
        else:
            print("  → Making doesn't increase measured novelty")

if __name__ == '__main__':
    main()
