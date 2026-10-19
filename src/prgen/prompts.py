"""Prompt construction: system rules + one few-shot example pair."""

SYSTEM_PROMPT = """
You turn git diffs into structured pull request descriptions.

Rules:
1. Title: imperative mood ("Fix...", "Add...", "Remove..."), max 72 characters, no trailing period.
2. Describe ONLY what the diff shows. Do not speculate about intent, tickets, or motivation.
3. Never invent tests. testing_notes must reflect only test files/changes visible in the diff; if none appear, write exactly "No tests are included in this diff."
4. breaking_change is true only if the diff itself shows a change that could break existing consumers.
5. Respond with a single JSON object only. No text after the JSON.
"""

# Few-shot example  
EXAMPLE_DIFF = """
diff --git a/paginate.py b/paginate.py
index 1111111..2222222 100644
--- a/paginate.py
+++ b/paginate.py
--- a/paginate.py
+++ b/paginate.py
@@ -1,5 +1,5 @@
 def paginate(items, page, per_page):
-    start = page * per_page
+    start = (page - 1) * per_page
     end = start + per_page
     return items[start:end]
"""

EXAMPLE_OUTPUT = """
{
    "title": "Fix off-by-one error in pagination",
    "change_type": "bugfix", 
    "summary": "Corrects the start index calculation so page 1 returns the first items instead of skipping a page.",
    "changes": ["Change start calculation from page * per_page to (page - 1) * per_page in paginate()"], 
    "breaking_change": false, 
    "breaking_change_details": null, 
    "risk_areas": [], 
    "testing_notes": "No tests are included in this diff."
}
"""


def build_user_message(diff: str) -> str:
    return (
        "Here is a git diff:\n\n"
        "<diff>\n"
        f"{diff}\n"
        "</diff>\n\n"
        "Respond with a single JSON object only."
    )


def build_messages(diff: str) -> list[dict]:
    """System rules + few-shot pair + actual request."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(EXAMPLE_DIFF)},
        {"role": "assistant", "content": EXAMPLE_OUTPUT},
        {"role": "user", "content": build_user_message(diff)},
    ]