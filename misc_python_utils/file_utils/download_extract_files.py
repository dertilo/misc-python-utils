import os
import re  # noqa: F401
from collections.abc import Callable
from pathlib import Path

from misc_python_utils.beartypes import Directory
from misc_python_utils.processing_utils.processing_utils import exec_command


def download_and_extract(
    base_url: str,
    file_name: str,
    data_dir: Directory,
    verbose: bool = False,
    remove_zipped: bool = False,
) -> str | None:
    """
    formerly called "download_data"
    """
    file = data_dir + "/" + file_name  # noqa: F841

    suffixes = [".zip", ".ZIP", ".tar.gz", ".tgz", ".gz", ".GZ", ".tar", ".TAR"]
    regex = r"|".join([f"(?:{s})" for s in suffixes])
    extract_folder = re.sub(regex, "", file)
    assert extract_folder != file

    if not Path(extract_folder).is_dir():
        wget_file(base_url + "/" + file_name, data_dir, verbose)
        Path(extract_folder).mkdir(exist_ok=True)
        extract_file(file, extract_folder, get_build_extract_command_fun(file))
        if remove_zipped:
            Path(file).unlink()
    return extract_folder


def get_build_extract_command_fun(file: str) -> Callable:  # noqa: C901,WPS231
    if any(file.endswith(suf) for suf in [".zip", ".ZIP"]):

        def fun(dirr, file):  # noqa: ANN001, ANN202
            return f"unzip -d {dirr} {file}"

    elif any(file.endswith(suf) for suf in [".tar.gz", ".tgz"]):

        def fun(dirr, file):  # noqa: ANN001, ANN202
            return f"tar xzf {file} -C {dirr}"

    elif any(file.endswith(suf) for suf in [".tar", ".TAR"]):

        def fun(dirr, file):  # noqa: ANN001, ANN202
            return f"tar xf {file} -C {dirr}"

    elif any(file.endswith(suf) for suf in [".gz", ".GZ"]):

        def fun(dirr, file):  # noqa: ANN001, ANN202
            return f"gzip -dc {file} {dirr}"

    else:
        raise NotImplementedError
    return fun


def extract_file(
    file: str,
    extract_folder: str,
    build_extract_command_fun: Callable,
) -> None:
    cmd = build_extract_command_fun(extract_folder, file)
    _, stderr = exec_command(cmd)
    assert len(stderr) == 0, f"{cmd=}: {stderr=}"


def wget_file(  # noqa: PLR0913
    url: str,
    data_folder: str,
    verbose: bool = False,
    file_name: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> None:
    # TODO(tilo): wget.download cannot continue ??
    passw = f" --password {password} " if password is not None else ""
    user = f' --user "{user}" ' if user is not None else ""
    quiet = " -q " if not verbose else ""
    if file_name is None:
        file_name = url.split("/")[-1]
    file = f"{data_folder}/{file_name}"
    os.makedirs(data_folder, exist_ok=True)  # noqa: PTH103
    if Path(file).is_file():  # noqa: PTH113
        cmd = f'wget -O {file} -c -N{quiet}{passw}{user} -P {data_folder} "{url}"'
    else:
        cmd = f'wget -O {file} -c {quiet}{passw}{user} -P {data_folder} "{url}"'

    print(f"{cmd=}")  # noqa: T201
    os.system(cmd)  # noqa: S605
    # TODO: why is subprocess not working?
    # download_output = exec_command(cmd)
    # if err_code != 0:
    #     raise FileNotFoundError(f"could not download {url}")


# def main():  # noqa: ANN201
#     file_name = "/test-other.tar.gz"
#     base_url = "http://www.openslr.org/resources/12"
#     download_data(
#         base_url,
#         file_name,
#         "/tmp/test_data",  # noqa: S108
#         unzip_it=True,
#         verbose=True,  # noqa: S108, COM812
#     )  # noqa: S108


# if __name__ == "__main__":
#     main()
