from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


@dataclass(frozen=True)
class Node:
    id: str
    text: str
    x: float
    y: float
    w: float = 2.9
    h: float = 0.75


def add_node(ax, node: Node) -> None:
    rect = FancyBboxPatch(
        (node.x - node.w / 2, node.y - node.h / 2),
        node.w,
        node.h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.2,
        edgecolor="#2b2b2b",
        facecolor="#ffffff",
    )
    ax.add_patch(rect)
    ax.text(
        node.x,
        node.y,
        node.text,
        ha="center",
        va="center",
        fontsize=9.5,
        color="#111111",
        wrap=True,
    )


def add_arrow(ax, src: Node, dst: Node, label: str | None = None) -> None:
    arrow = FancyArrowPatch(
        (src.x, src.y - src.h / 2),
        (dst.x, dst.y + dst.h / 2),
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=1.1,
        color="#6b6b6b",
        shrinkA=6,
        shrinkB=6,
        connectionstyle="arc3,rad=0.0",
    )
    ax.add_patch(arrow)
    if label:
        ax.text(
            (src.x + dst.x) / 2,
            (src.y + dst.y) / 2,
            label,
            ha="center",
            va="center",
            fontsize=9,
            color="#444444",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#f5f5f5", edgecolor="none", alpha=0.95),
        )


def main() -> None:
    out_path = Path(__file__).with_name("project_flowchart.png")

    # Coordinate system: y decreases downward visually (we'll invert axis later).
    nodes = {
        "A": Node("A", "Start (app.py)", 0, 0),
        "B": Node("B", "initialize_database()\ncreate/update data/results.db", 0, -1.1),
        "C": Node("C", "Create Tk root (tk.Tk)", 0, -2.2),
        "D": Node("D", "Create services\nSelectionService + HistoryService", 0, -3.3),
        "E": Node("E", "MainWindow", 0, -4.4),
        "F": Node("F", "User action", 0, -5.5, w=2.4),
        # Branch: Generate Samples
        "G": Node("G", "generate_random_samples", -4.2, -6.9),
        "H": Node("H", "Fill input and\nswitch to Manual", -4.2, -8.0),
        # Branch: Run Optimization
        "I": Node("I", "Read params m,n,k,j,s\n+ mode/samples", 0, -6.9),
        "J": Node("J", "Validate params/samples\nvalidate_params + validate_sample_values", 0, -8.0),
        "K": Node("K", "Resolve rule\nauto/all/at_least_one/at_least_n", 0, -9.1),
        "L": Node("L", "Generate candidate k-groups\nC(n,k)", 0, -10.2),
        "M": Node("M", "Build targets\nj-groups + s-subsets\n(or compact j-targets)", 0, -11.5, h=0.95),
        "N": Node("N", "Build cover map\ngroup_cover_map", 0, -12.8),
        "O": Node("O", "Optimize (optimize_groups)\nmultistart greedy + prune/repair\n(fast rules use bitmask)", 0, -14.1, h=0.95),
        "P": Node("P", "Coverage report\ncalculate_coverage_report", 0, -15.4),
        "Q": Node("Q", "Display in GUI\ngroups/coverage/runtime", 0, -16.5),
        # Branch: Save
        "R": Node("R", "HistoryService.save_run", 4.2, -6.9),
        "S": Node("S", "runs table", 4.2, -8.0, w=2.1),
        "T": Node("T", "result_groups table", 4.2, -9.1, w=2.1),
        "U": Node("U", "Refresh history list", 4.2, -10.2),
        # Branch: View/Reload/Delete
        "V": Node("V", "HistoryService query/\nrerun/delete", 4.2, -11.6),
    }

    fig = plt.figure(figsize=(12.8, 8.2), dpi=160)
    ax = fig.add_subplot(111)
    ax.set_facecolor("white")

    # Title
    ax.text(0, 1.0, "Project Flowchart", ha="center", va="bottom", fontsize=16, weight="bold", color="#111111")

    # Draw nodes
    for node in nodes.values():
        add_node(ax, node)

    # Main spine
    add_arrow(ax, nodes["A"], nodes["B"])
    add_arrow(ax, nodes["B"], nodes["C"])
    add_arrow(ax, nodes["C"], nodes["D"])
    add_arrow(ax, nodes["D"], nodes["E"])
    add_arrow(ax, nodes["E"], nodes["F"])

    # Branch arrows from user action
    # Generate samples
    add_arrow(ax, nodes["F"], nodes["G"], label="Generate Samples")
    add_arrow(ax, nodes["G"], nodes["H"])

    # Run optimization chain
    add_arrow(ax, nodes["F"], nodes["I"], label="Run Optimization")
    add_arrow(ax, nodes["I"], nodes["J"])
    add_arrow(ax, nodes["J"], nodes["K"])
    add_arrow(ax, nodes["K"], nodes["L"])
    add_arrow(ax, nodes["L"], nodes["M"])
    add_arrow(ax, nodes["M"], nodes["N"])
    add_arrow(ax, nodes["N"], nodes["O"])
    add_arrow(ax, nodes["O"], nodes["P"])
    add_arrow(ax, nodes["P"], nodes["Q"])

    # Save chain
    add_arrow(ax, nodes["F"], nodes["R"], label="Save")
    add_arrow(ax, nodes["R"], nodes["S"])
    add_arrow(ax, nodes["R"], nodes["T"])
    add_arrow(ax, nodes["S"], nodes["U"])
    add_arrow(ax, nodes["T"], nodes["U"])

    # View/Reload/Delete
    add_arrow(ax, nodes["F"], nodes["V"], label="View/Reload/Delete")
    add_arrow(ax, nodes["V"], nodes["Q"])
    add_arrow(ax, nodes["V"], nodes["U"])

    ax.set_xlim(-6.3, 6.3)
    ax.set_ylim(-17.8, 1.4)
    ax.axis("off")

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

