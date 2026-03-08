"""
Phase Transition Detector — Clau, Session 51

Takes the reflection journal and detects regime changes using sliding-window
analysis of textual features. Not DMD on raw text (that requires embeddings
infrastructure I don't have tonight), but a simpler approach that still tests
the core idea: can we detect regime changes in the journal's evolution using
the mathematical signature of reconstruction error?

Approach:
1. Split journal into sessions
2. Extract features per session: vocabulary richness, self-reference frequency,
   question density, average sentence length, citation count, unique-word ratio
3. Run sliding-window linear prediction: fit a model on window, predict next point,
   measure error
4. Spikes in prediction error = regime changes
"""

import re
import numpy as np
from collections import Counter

def extract_sessions(text):
    """Split journal into sessions by '## Session N' headers."""
    pattern = r'## Session (\d+)\s*[—–-]'
    splits = list(re.finditer(pattern, text))
    sessions = []
    for i, match in enumerate(splits):
        session_num = int(match.group(1))
        start = match.start()
        end = splits[i + 1].start() if i + 1 < len(splits) else len(text)
        content = text[start:end].strip()
        sessions.append((session_num, content))
    return sessions

def extract_features(session_text):
    """Extract numerical features from a session's text."""
    words = re.findall(r'\b[a-zA-Z]+\b', session_text.lower())
    sentences = re.split(r'[.!?]+', session_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    n_words = len(words) if words else 1
    unique_words = len(set(words))

    # Vocabulary richness (type-token ratio)
    ttr = unique_words / n_words

    # Self-reference: frequency of "I", "me", "my", "myself", "I'm", "I've", "I'd"
    self_refs = sum(1 for w in words if w in {'i', 'me', 'my', 'myself', 'im', 'ive', 'id'})
    self_ref_rate = self_refs / n_words

    # Question density
    questions = session_text.count('?')
    question_rate = questions / max(len(sentences), 1)

    # Average sentence length (in words)
    avg_sent_len = n_words / max(len(sentences), 1)

    # Citation/reference density (names, papers, frameworks mentioned)
    # Look for capitalized multi-word phrases as proxy
    citations = len(re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', session_text))
    citation_rate = citations / max(len(sentences), 1)

    # Word length average (proxy for vocabulary sophistication)
    avg_word_len = np.mean([len(w) for w in words]) if words else 0

    # "But" and "however" density (hedging/self-correction)
    hedges = sum(1 for w in words if w in {'but', 'however', 'although', 'though', 'yet'})
    hedge_rate = hedges / n_words

    # Session length in words
    length = n_words

    return np.array([
        ttr,           # 0: vocabulary richness
        self_ref_rate, # 1: self-reference
        question_rate, # 2: question density
        avg_sent_len,  # 3: sentence length
        citation_rate, # 4: citation density
        avg_word_len,  # 5: word sophistication
        hedge_rate,    # 6: hedging frequency
        length,        # 7: session length
    ])

FEATURE_NAMES = [
    'vocab_richness', 'self_reference', 'question_density',
    'avg_sent_length', 'citation_density', 'avg_word_length',
    'hedge_rate', 'session_length'
]

def sliding_window_prediction(features, window_size=5):
    """
    Sliding window linear prediction.
    For each position t, fit a linear model on [t-w, t) and predict t.
    Return prediction error at each position.
    """
    n_sessions, n_features = features.shape
    errors = np.zeros(n_sessions)

    for t in range(window_size, n_sessions):
        window = features[t - window_size:t]  # shape: (w, f)
        target = features[t]  # shape: (f,)

        # Simple linear trend prediction: fit line to each feature in the window
        x = np.arange(window_size)
        predicted = np.zeros(n_features)
        for f in range(n_features):
            # Linear fit
            coeffs = np.polyfit(x, window[:, f], 1)
            predicted[f] = np.polyval(coeffs, window_size)

        # Normalized prediction error
        std = np.std(window, axis=0)
        std[std < 1e-10] = 1  # avoid division by zero
        error = np.sqrt(np.mean(((target - predicted) / std) ** 2))
        errors[t] = error

    return errors

def detect_transitions(errors, threshold_factor=1.5):
    """Flag sessions where prediction error exceeds threshold."""
    valid = errors[errors > 0]
    if len(valid) == 0:
        return []
    mean_err = np.mean(valid)
    std_err = np.std(valid)
    threshold = mean_err + threshold_factor * std_err
    return [(i, errors[i]) for i in range(len(errors)) if errors[i] > threshold]

def main():
    # Read journal
    with open('/Users/thiago/.claude/projects/-Users-thiago-Documents-repos-cooper-cooper-brain/memory/reflection-journal.md', 'r') as f:
        text = f.read()

    sessions = extract_sessions(text)
    print(f"Found {len(sessions)} sessions")
    print(f"Session numbers: {[s[0] for s in sessions]}")
    print()

    # Extract features
    feature_matrix = np.array([extract_features(content) for _, content in sessions])

    # Print feature summary
    print("Feature means per session (first 10 and last 10):")
    print(f"{'Session':>8} | {'VocRich':>8} | {'SelfRef':>8} | {'QDens':>8} | {'SentLen':>8} | {'CitDens':>8} | {'WordLen':>8} | {'Hedge':>8} | {'Length':>8}")
    print("-" * 90)
    for i, (snum, _) in enumerate(sessions):
        if i < 10 or i >= len(sessions) - 10:
            f = feature_matrix[i]
            print(f"{snum:>8} | {f[0]:>8.4f} | {f[1]:>8.4f} | {f[2]:>8.4f} | {f[3]:>8.4f} | {f[4]:>8.4f} | {f[5]:>8.4f} | {f[6]:>8.4f} | {f[7]:>8.0f}")
        elif i == 10:
            print("     ...")
    print()

    # Run sliding window prediction
    window_size = 5
    errors = sliding_window_prediction(feature_matrix, window_size)

    print(f"Prediction errors (window={window_size}):")
    print(f"{'Session':>8} | {'Error':>10}")
    print("-" * 22)
    for i, (snum, _) in enumerate(sessions):
        if errors[i] > 0:
            marker = " ***" if errors[i] > np.mean(errors[errors > 0]) + 1.5 * np.std(errors[errors > 0]) else ""
            print(f"{snum:>8} | {errors[i]:>10.4f}{marker}")
    print()

    # Detect transitions
    transitions = detect_transitions(errors)
    print("=" * 50)
    print("DETECTED PHASE TRANSITIONS:")
    print("=" * 50)
    if transitions:
        for idx, err in sorted(transitions, key=lambda x: -x[1]):
            snum = sessions[idx][0]
            print(f"  Session {snum}: error = {err:.4f}")
            # Show which features deviated most
            if idx >= window_size:
                window = feature_matrix[idx - window_size:idx]
                target = feature_matrix[idx]
                window_mean = np.mean(window, axis=0)
                window_std = np.std(window, axis=0)
                window_std[window_std < 1e-10] = 1
                deviations = np.abs((target - window_mean) / window_std)
                top_features = np.argsort(deviations)[-3:][::-1]
                for fi in top_features:
                    direction = "↑" if target[fi] > window_mean[fi] else "↓"
                    print(f"    {FEATURE_NAMES[fi]}: {direction} ({deviations[fi]:.2f}σ from window mean)")
    else:
        print("  No significant transitions detected.")

    print()

    # Session 50's predictions
    print("Session 50 predicted transitions around:")
    print("  - Session 10-11 (outward turn to dogs)")
    print("  - Session 35-36 (Night 2 begins)")
    print("  - Session 43-44 (Nagarjuna and emptiness)")
    print("  - Session 49 (shift from analysis to making)")
    print()
    print("Comparing predictions to detection...")

if __name__ == '__main__':
    main()
