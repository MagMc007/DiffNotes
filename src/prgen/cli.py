"""diffnotes CLI: git diff -> validated PR description."""

import argparse
import sys

from .diff import read_git_diff, filter_diff
from .errors import InputError, ProviderError, GenerationFailed, ProviderAuthError
from .generate import generate_pr_description
from .prompts import build_messages
from .providers.openrouter import OpenRouterProvider
from .render import to_markdown

def main() -> int:
    parser = argparse.ArgumentParser(prog="diffnotes", description="Turn a git diff into a PR description.")
    parser.add_argument("--staged", action="store_true", help="use `git diff --staged`")
    parser.add_argument("--base", help="diff against this base branch/ref")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    try:
        raw_diff = read_git_diff(staged=args.staged, base=args.base)
        clean_diff, skipped = filter_diff(raw_diff)
        for s in skipped:
            print(f"skipped: {s}", file=sys.stderr)

        provider = OpenRouterProvider()
        pr = generate_pr_description(provider, build_messages(clean_diff))

        if args.format == "json":
            print(pr.model_dump_json(indent=2))
        else:
            print(to_markdown(pr))
        return 0

    except InputError as e:
        print(f"error: {e}", file=sys.stderr)
        return e.exit_code  # 2
    except ProviderAuthError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except (ProviderError, GenerationFailed) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())