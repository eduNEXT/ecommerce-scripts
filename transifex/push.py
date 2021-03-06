#!/usr/bin/env python3
"""
This script can be used to automatically extract translation strings,
commit, push, and merge them to their respective repos, and then push them to Transifex.

To use, export an environment variable `GITHUB_ACCESS_TOKEN`. The token requires
GitHub's "repo" scope.

Run the script from the root of this repo.

    python transifex/push.py git@github.com:edx/course-discovery.git

If you want to use a custom merge method pass the --merge-method option.

    python transifex/push.py git@github.com:edx/course-discovery.git --merge-method rebase
"""
from argparse import ArgumentParser

from utils import DEFAULT_MERGE_METHOD, MERGE_METHODS, logger, repo_context

# The name of the branch to use.
BRANCH_NAME = 'transifex-bot-update-translation-strings'

# The commit message to use.
MESSAGE = 'fix(i18n): update translation strings'


def push(clone_url, repo_owner, merge_method=DEFAULT_MERGE_METHOD, skip_commit=False, skip_check_changes=False):
    """Extracts translations for the given repo, commits them, pushes them to GitHub, opens a PR, waits for status
        checks to pass, merges the PR, deletes the branch, and pushes the updated translation files to Transifex.
    """
    with repo_context(clone_url, repo_owner, BRANCH_NAME, MESSAGE, merge_method=merge_method) as repo:
        logger.info('Extracting translations for [%s].', repo.name)
        repo.extract_translations()

        if not skip_commit:
            repo.commit_push_and_open_pr(skip_check_changes)
            if repo.pr and repo.merge_pr() and repo.pr.is_merged():
                push_translations_to_transifex(repo)
        else:
            push_translations_to_transifex(repo)


def push_translations_to_transifex(repo):
    """
    Calls the push translations make target to push new translation strings to Transifex.
    """
    repo.push_translations()


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument(
        'clone_url',
        help='URL to use to clone the repository.'
    )
    parser.add_argument(
        'repo_owner',
        help='This is the user/team that will be pinged when errors occur.'
    )
    parser.add_argument(
        '--merge-method',
        choices=MERGE_METHODS,
        default=DEFAULT_MERGE_METHOD,
        help='Method to use when merging the PR. See https://developer.github.com/v3/pulls/#merge-a-pull-request-merge-button for details.'
    )
    parser.add_argument(
        '--skip_commit',
        action='store_true',
        help='Use this if you do not want to commit changes to repo.'
    )
    parser.add_argument(
        '--skip-check-changes',
        action='store_true',
        help='Skip the check changes step.'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    push(args.clone_url, args.repo_owner, merge_method=args.merge_method, skip_commit=args.skip_commit,
         skip_check_changes=args.skip_check_changes)
