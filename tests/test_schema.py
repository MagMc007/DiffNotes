import pytest
from pydantic import ValidationError
from src.prgen.schema import PRDescription

def make_valid(**over):
    base = dict(
        title="Fix off-by-one error in pagination",
        change_type="bugfix",
        summary="Corrects the start index calculation so page 1 returns the first items.",
        changes=["Change start calculation in paginate()"],
        breaking_change=False,
        testing_notes="No tests are included in this diff.",
    )
    base.update(over)
    return PRDescription(**base)

def test_valid():
    make_valid()

def test_title_too_long():
    with pytest.raises(ValidationError):
        make_valid(title="x" * 73)

def test_trailing_period():
    with pytest.raises(ValidationError):
        make_valid(title="Fix the bug.")

def test_breaking_without_details():
    with pytest.raises(ValidationError):
        make_valid(breaking_change=True)

def test_details_without_breaking():
    with pytest.raises(ValidationError):
        make_valid(breaking_change_details="Removed the old API")

if __name__ == "__main__":
    test_valid(); test_title_too_long(); test_trailing_period()
    test_breaking_without_details(); test_details_without_breaking()
    print("all pass")