import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from buildable_dataclasses.buildable_data import BuildableData

from misc_python_utils.prefix_suffix import PrefixSuffix
from misc_python_utils.slugification import CasedNameSlug

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html

# TODO: got "circular" dependency back to buildable-dataclasses here!


@dataclass
class GitRepoContent(BuildableData):
    git_repo: str  # = "git@gitlab.cc-asp.orgname.de:group/reponame.git"
    base_dir: PrefixSuffix  # = field(default_factory=lambda: PrefixSuffix("processed_raw_data","GIT_REPOS"))
    do_pull: bool = False
    commit_sha: str | None = field(init=False, repr=True, default=None)
    name: CasedNameSlug = field(init=False)

    def __post_init__(self):
        repo_name = self.git_repo.split("/")[-1].replace(".git", "").replace("_", "-")
        self.name = f"{repo_name}-git-repo"

    @property
    def _is_data_valid(self) -> bool:
        return not self.do_pull and Path(f"{self.data_dir}/.git").is_dir()

    def _build_data(self) -> Any:
        from git import (
            Repo,  # not top-level cause inside docker-container this complains for not having git installed!
        )

        if not Path(f"{self.data_dir}/.git").is_dir():
            repo = Repo.clone_from(self.git_repo, self.data_dir)
            logger.info(f"cloning {self.git_repo} into {self.data_dir}")
            if self.commit_sha is not None:
                repo.git.checkout(self.commit_sha)
            else:
                self.commit_sha = repo.head.object.hexsha

        elif self.do_pull:
            repo = Repo(self.data_dir).remote().pull()
            self.commit_sha = repo.head.object.hexsha
        else:
            raise NotImplementedError

        # write_json(f"{self.data_dir}/info.json", asdict(self))
