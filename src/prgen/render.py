""" render a validated PRreview to Markdown """
from .schema import PRDescription

def to_markdown(pr: PRDescription) -> str: 
    lines = [
        f"# {pr.title}",
        "",
        f"**Type:** {pr.change_type.value}",
        "",
        pr.summary,
        "",
        "## Changes",
    ]
    lines += [f"- {c}" for c in pr.changes]

    if pr.risk_areas:
        lines += ["", "## Risk Areas"]
        lines += [f"- {r}" for r in pr.risk_areas]

    if pr.breaking_change:
        lines += [
            "",
            "## ⚠️ Breaking Change",
            "",
            pr.breaking_change_details or "Details not provided.",
        ]

    lines += ["", "## Testing", "", pr.testing_notes]

    return "\n".join(lines) + "\n"