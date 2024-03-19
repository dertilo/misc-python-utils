import dataclasses
import inspect
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

from result import Err, Ok, Result

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html

try:
    from git import InvalidGitRepositoryError, Remote, Repo
except ImportError:
    logger.warning("no git installed!")
    Repo, Remote = None, None


@dataclass
class GitRepoState:
    # repo_path: Path = field(
    #     default_factory=lambda: BASE_PATHES.get("repo_path", Path.cwd()),
    # )  # if you're not running python from the git-repos root dir you need to set this "repo_path"
    repo: Repo = field(init=True, repr=False)
    must_be_clean: bool = True

    @property
    def git_root_path(self) -> str:
        return self.repo.git.rev_parse("--show-toplevel")

    @property
    def repo_url(self) -> str:
        return self._origin.url

    @property
    def _origin(self) -> Remote:
        return self.repo.remotes["origin"]

    @property
    def commit_sha(self) -> str:
        if self.repo.is_dirty() and self.must_be_clean:
            msg = "Repo is not clean! Commit your changes!"
            raise AssertionError(msg)
        return self.repo.head.object.hexsha  # noqa: WPS219

    @property
    def origin_https_url(self) -> str:
        git_remote_url = self.repo_url
        assert git_remote_url.startswith("git@")
        assert git_remote_url.endswith(".git")
        return (
            git_remote_url.replace("git@", "https://")
            .replace(".git", "")
            .replace(":", "/")  # is this gitlab specific?
        )

    def add_and_commit_file(self, file: Path) -> None:
        self.repo.git.add(str(file))
        self.repo.index.commit(file.name)


class NoTraceException(Exception):  # noqa: N818 # TODO: move to some utils upstream
    def __init__(self, *args: object) -> None:
        sys.tracebacklimit = -1
        super().__init__(*args)


class UncommittedChanges(Exception):  # noqa: N818
    __match_args__ = ("msg",)

    def __init__(self, class_file: str) -> None:
        self.msg = f"{class_file} has uncommitted changes!"
        super().__init__(self.msg)


def permanent_link_from_class(
    clazz: type,
) -> Result[str, str | UncommittedChanges | ImportError]:
    class_file = inspect.getfile(clazz)
    repo = find_git_repo(Path(class_file).parent)
    if repo.is_err():
        return repo
    git_repo_state = GitRepoState(repo=repo.ok(), must_be_clean=False)

    if file_has_uncommitted_changes(
        class_file, repo=git_repo_state.repo  # noqa: COM812, SLF001
    ):  # noqa: SLF001
        # TODO: check if file is added to git staging!
        return Err(UncommittedChanges(class_file))

    sha = git_repo_state.commit_sha
    git_remote_url = git_repo_state.origin_https_url
    class_file_suffix = class_file.replace(git_repo_state.git_root_path, "")
    class_line = inspect.findsource(clazz)[
        1
    ]  # see: https://stackoverflow.com/questions/41971660/python-how-to-programmatically-get-line-number-of-class-definition
    if dataclasses.is_dataclass(clazz):
        class_line += 2  # don't ask me why but somehow its 2 lines "early"
    file_and_line = f"{class_file_suffix}#L{class_line}"
    return Ok(f"{git_remote_url}/blob/{sha}{file_and_line}")


def file_has_uncommitted_changes(class_file: Path | str, repo: Repo) -> bool:
    index = repo.index
    gitdiff = index.diff(None, paths=class_file)
    return len(gitdiff) > 0 and str(class_file).endswith(gitdiff[0].a_path)


def find_git_repo(
    path: Path,
) -> Result[Repo, str | ImportError]:
    if Repo is None:
        return Err(ImportError("no git installed!"))

    for _ in range(100):
        try:
            repo = Repo(path)
            return Ok(repo)  # noqa: TRY300
        except InvalidGitRepositoryError:
            path = path.parent
    return Err(
        "did not find git repo",
    )  # not wrapping the exception here, cause who cares
