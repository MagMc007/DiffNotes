from src.prgen.schema import PRDescription
from src.prgen.render import to_markdown

pr = PRDescription(
    title="Fix off-by-one error in pagination",
    change_type="bugfix",
    summary="Corrects the start index calculation so page 1 returns the first items instead of skipping a page.",
    changes=["Change start calculation in paginate()"],
    breaking_change=False,
    testing_notes="No tests are included in this diff.",
)
print(to_markdown(pr))