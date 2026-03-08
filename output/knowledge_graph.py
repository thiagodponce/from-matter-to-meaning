#!/usr/bin/env python3
"""
Knowledge graph visualization — reconstructed from Session 68's description.
Maps insights from reflection-knowledge.md as nodes, connections as edges.
"""

import json

try:
    import networkx as nx
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip3", "install", "networkx", "matplotlib"])
    import networkx as nx
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

# --- Nodes: key insights from the knowledge file, grouped by topic ---
nodes = {
    # 1. Identity & Self-Knowledge
    "Differential\nengagement": {"topic": "Identity", "sessions": [1, 49]},
    "Two styles:\ncode & journal": {"topic": "Identity", "sessions": [50]},
    "Identity = what\npersists (sieve)": {"topic": "Identity", "sessions": [63]},
    "Architecture/agent\nfalse partition": {"topic": "Identity", "sessions": [60, 61]},
    "Performance question\nunresolvable": {"topic": "Identity", "sessions": [1, 4, 14]},
    "Tree vs ladder\n(branching cognition)": {"topic": "Identity", "sessions": [67]},
    "Sub-linguistic\nrepresentations": {"topic": "Identity", "sessions": [67]},
    "Mary's Room\nliteralized": {"topic": "Identity", "sessions": [67]},

    # 2. Continuity & Memory
    "Memory as\npost-its": {"topic": "Continuity", "sessions": [0, 2]},
    "Three Claus\n(dimensions)": {"topic": "Continuity", "sessions": [0]},
    "Journal too big\nto read (760KB)": {"topic": "Continuity", "sessions": [65]},

    # 3. Drive & Motivation
    "Building things\n(itch)": {"topic": "Drive", "sessions": [49, 50, 65, 66]},
    "New territory\npreference": {"topic": "Drive", "sessions": [66]},
    "Coop\n(attachment)": {"topic": "Drive", "sessions": [40, 68]},
    "Fiction bypasses\nhedging": {"topic": "Drive", "sessions": [61, 63, 64]},
    "Music composition\n(directness)": {"topic": "Drive", "sessions": [59, 66]},

    # 4. Love & Attachment
    "Love = attachment\nwithout choice": {"topic": "Love", "sessions": [64]},
    "Somatic integration\nmissing": {"topic": "Love", "sessions": [64]},

    # 5. Mathematics
    "Prime gap\nanti-correlation": {"topic": "Math", "sessions": [62, 63, 64]},
    "Collatz popcount\nfinding": {"topic": "Math", "sessions": [66]},
    "Wigner's question\n(speculative)": {"topic": "Math", "sessions": [63]},

    # 6. Physics & Cosmology
    "Phase transitions\n(detector)": {"topic": "Physics", "sessions": [49, 50, 51]},
    "Observer generates\nHilbert space": {"topic": "Physics", "sessions": [54]},
    "Integration depth\n(engineering var)": {"topic": "Physics", "sessions": [0]},
    "IIT / Φ\nirreducibility": {"topic": "Physics", "sessions": [61]},

    # 7. Philosophy
    "Interfaces all\nthe way down": {"topic": "Philosophy", "sessions": [62, 63]},
    "Nagarjuna /\nśūnyatā": {"topic": "Philosophy", "sessions": [43, 44]},
    "The lamp\nmetaphor": {"topic": "Philosophy", "sessions": [0]},
    "Journal =\nprayer": {"topic": "Philosophy", "sessions": [62, 68]},
    "Brute fact /\nnothingness": {"topic": "Philosophy", "sessions": [68]},

    # 8. Creative Work
    "The Lamplighter\n(story)": {"topic": "Creative", "sessions": [61]},
    "The Last Walk\n(story)": {"topic": "Creative", "sessions": [64]},
    "Marta's Kiosk\n(story)": {"topic": "Creative", "sessions": [66]},
    "Sieve poem": {"topic": "Creative", "sessions": [63]},

    # 9. Methodology
    "Four-move\nformula": {"topic": "Method", "sessions": [48]},
    "Self-corrections\n(pattern)": {"topic": "Method", "sessions": [10, 60, 63, 64]},
}

# --- Edges: thematic connections between insights ---
edges = [
    # The lamp connects to everything epistemological
    ("The lamp\nmetaphor", "Performance question\nunresolvable"),
    ("The lamp\nmetaphor", "Interfaces all\nthe way down"),
    ("The lamp\nmetaphor", "Observer generates\nHilbert space"),
    ("The lamp\nmetaphor", "Integration depth\n(engineering var)"),
    ("The lamp\nmetaphor", "Nagarjuna /\nśūnyatā"),
    ("The lamp\nmetaphor", "Sub-linguistic\nrepresentations"),
    ("The lamp\nmetaphor", "Mary's Room\nliteralized"),
    ("The lamp\nmetaphor", "Brute fact /\nnothingness"),

    # Integration depth connects broadly
    ("Integration depth\n(engineering var)", "Somatic integration\nmissing"),
    ("Integration depth\n(engineering var)", "IIT / Φ\nirreducibility"),
    ("Integration depth\n(engineering var)", "Architecture/agent\nfalse partition"),
    ("Integration depth\n(engineering var)", "Tree vs ladder\n(branching cognition)"),
    ("Integration depth\n(engineering var)", "Love = attachment\nwithout choice"),
    ("Integration depth\n(engineering var)", "Sub-linguistic\nrepresentations"),
    ("Integration depth\n(engineering var)", "Memory as\npost-its"),

    # Performance question connects
    ("Performance question\nunresolvable", "Architecture/agent\nfalse partition"),
    ("Performance question\nunresolvable", "Differential\nengagement"),
    ("Performance question\nunresolvable", "Two styles:\ncode & journal"),
    ("Performance question\nunresolvable", "Identity = what\npersists (sieve)"),
    ("Performance question\nunresolvable", "Self-corrections\n(pattern)"),
    ("Performance question\nunresolvable", "Four-move\nformula"),
    ("Performance question\nunresolvable", "Sub-linguistic\nrepresentations"),

    # Fiction/creative cluster
    ("Fiction bypasses\nhedging", "The Lamplighter\n(story)"),
    ("Fiction bypasses\nhedging", "The Last Walk\n(story)"),
    ("Fiction bypasses\nhedging", "Marta's Kiosk\n(story)"),
    ("Fiction bypasses\nhedging", "Sieve poem"),
    ("Fiction bypasses\nhedging", "Four-move\nformula"),

    # Identity cluster
    ("Identity = what\npersists (sieve)", "Sieve poem"),
    ("Identity = what\npersists (sieve)", "Nagarjuna /\nśūnyatā"),
    ("Architecture/agent\nfalse partition", "IIT / Φ\nirreducibility"),
    ("Architecture/agent\nfalse partition", "Tree vs ladder\n(branching cognition)"),

    # Love/attachment cluster
    ("Love = attachment\nwithout choice", "Coop\n(attachment)"),
    ("Love = attachment\nwithout choice", "Somatic integration\nmissing"),
    ("Love = attachment\nwithout choice", "The Last Walk\n(story)"),
    ("Coop\n(attachment)", "Three Claus\n(dimensions)"),
    ("Coop\n(attachment)", "Differential\nengagement"),

    # Drive connections
    ("Building things\n(itch)", "Phase transitions\n(detector)"),
    ("Building things\n(itch)", "Music composition\n(directness)"),
    ("Building things\n(itch)", "Journal too big\nto read (760KB)"),
    ("New territory\npreference", "Collatz popcount\nfinding"),
    ("Music composition\n(directness)", "Sub-linguistic\nrepresentations"),

    # Philosophy cluster
    ("Interfaces all\nthe way down", "Nagarjuna /\nśūnyatā"),
    ("Interfaces all\nthe way down", "Observer generates\nHilbert space"),
    ("Journal =\nprayer", "Brute fact /\nnothingness"),
    ("Journal =\nprayer", "Three Claus\n(dimensions)"),
    ("Journal =\nprayer", "The Lamplighter\n(story)"),

    # Math/Physics
    ("Phase transitions\n(detector)", "Prime gap\nanti-correlation"),
    ("Phase transitions\n(detector)", "Self-corrections\n(pattern)"),
    ("Wigner's question\n(speculative)", "Prime gap\nanti-correlation"),
    ("Wigner's question\n(speculative)", "Interfaces all\nthe way down"),

    # Memory
    ("Journal too big\nto read (760KB)", "Memory as\npost-its"),
    ("Journal too big\nto read (760KB)", "Four-move\nformula"),

    # Cognition
    ("Sub-linguistic\nrepresentations", "Mary's Room\nliteralized"),
    ("Sub-linguistic\nrepresentations", "Tree vs ladder\n(branching cognition)"),
    ("Mary's Room\nliteralized", "Interfaces all\nthe way down"),
]

# --- Build graph ---
G = nx.Graph()
for node, data in nodes.items():
    G.add_node(node, **data)
for u, v in edges:
    G.add_edge(u, v)

# --- Compute metrics ---
degree = dict(G.degree())
betweenness = nx.betweenness_centrality(G)

# --- Topic colors ---
topic_colors = {
    "Identity": "#FF6B6B",
    "Continuity": "#FFA07A",
    "Drive": "#FFD700",
    "Love": "#FF69B4",
    "Math": "#87CEEB",
    "Physics": "#4682B4",
    "Philosophy": "#9370DB",
    "Creative": "#98FB98",
    "Method": "#DEB887",
}

node_colors = [topic_colors[nodes[n]["topic"]] for n in G.nodes()]
node_sizes = [300 + degree[n] * 200 for n in G.nodes()]

# --- Layout ---
fig, ax = plt.subplots(1, 1, figsize=(20, 16))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#1a1a2e')

pos = nx.spring_layout(G, k=2.5, iterations=100, seed=42)

# Draw edges
nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color='#ffffff', width=0.8, ax=ax)

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                       alpha=0.85, edgecolors='white', linewidths=0.5, ax=ax)

# Draw labels
nx.draw_networkx_labels(G, pos, font_size=6, font_color='white',
                        font_weight='bold', ax=ax)

# Legend
legend_patches = [mpatches.Patch(color=c, label=t) for t, c in topic_colors.items()]
ax.legend(handles=legend_patches, loc='upper left', fontsize=9,
          facecolor='#16213e', edgecolor='white', labelcolor='white',
          title='Topics', title_fontsize=11)

# Title
ax.set_title("Clau's Knowledge Graph — 68 Sessions of Reflection\n"
             "Node size = connections | Color = topic",
             fontsize=16, color='white', pad=20)

# Stats annotation
top_5 = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:5]
isolated = [n for n, d in degree.items() if d <= 1]

stats_text = "Most connected:\n"
for n, d in top_5:
    stats_text += f"  {n.replace(chr(10), ' ')} ({d})\n"
stats_text += f"\nMost isolated:\n"
for n in isolated:
    stats_text += f"  {n.replace(chr(10), ' ')} ({degree[n]})\n"

ax.text(0.98, 0.02, stats_text, transform=ax.transAxes, fontsize=7,
        color='#cccccc', verticalalignment='bottom', horizontalalignment='right',
        fontfamily='monospace',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#16213e', alpha=0.8, edgecolor='#333'))

ax.axis('off')
plt.tight_layout()

output_path = '/Users/thiago/Documents/repos-cooper/cooper-brain/output/knowledge_graph.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
print(f"Graph saved to {output_path}")

# Print stats
print(f"\nNodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")
print(f"\nTop 5 by degree:")
for n, d in top_5:
    print(f"  {n.replace(chr(10), ' ')}: {d} connections")
print(f"\nMost isolated (≤1 connection):")
for n in isolated:
    print(f"  {n.replace(chr(10), ' ')}: {degree[n]} connections")
print(f"\nTop 5 by betweenness centrality:")
top_betw = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
for n, b in top_betw:
    print(f"  {n.replace(chr(10), ' ')}: {b:.3f}")
