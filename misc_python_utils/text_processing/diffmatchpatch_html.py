import diff_match_patch

from misc_python_utils.file_utils.readwrite_files import write_file


def diff_to_html_via_dmp(text1: str, text2: str) -> str:
    text1 = "\n".join(list(text1))  # TODO: why does dmp want it like this?
    text2 = "\n".join(list(text2))

    dmp = diff_match_patch.diff_match_patch()
    dmp.Diff_Timeout = 0
    orig_enc, pred_enc, enc = dmp.diff_linesToChars(text1, text2)
    diffs = dmp.diff_main(orig_enc, pred_enc, checklines=False)
    dmp.diff_charsToLines(diffs, enc)
    diffs_post = []
    for d in diffs:
        diffs_post.append((d[0], d[1].replace("\n", "")))  # noqa: PERF401

    diff_html = dmp.diff_prettyHtml(diffs_post)
    return diff_html  # noqa: RET504


if __name__ == "__main__":
    text = "NOT HAVING THE COURAGE OR THE INDUSTRY OF OUR NEIGHBOUR WHO WORKS LIKE A BUSY BEE IN THE WORLD OF MEN AND BOOKS SEARCHING WITH THE SWEAT OF HIS BROW FOR THE REAL BREAD OF LIFE WETTING THE OPEN PAGE BEFORE HIM WITH HIS TEARS PUSHING INTO THE WE HOURS OF THE NIGHT HIS QUEST ANIMATED BY THE FAIREST OF ALL LOVES THE LOVE OF TRUTH WE EASE OUR OWN INDOLENT CONSCIENCE BY CALLING HIM NAMES"
    text2 = "NOT HAVING THE COURAGE OR THE Bla OF OUR NEIGHBOR WHO WORKS LIKE A BUSY BEE IN THE OF MEN AND BOOKS SEARCHING WITH THE SWEAT OF HIS BROW some insertion FOR THE REAL BREAD OF LIFE WETTING THE OPEN PAGE BEFORE HIM WITH HIS TEARS PUSHING INTO THE WE HOURS OF THE NIGHT HIS QUEST ANIMATED BY THE FAIREST OF ALL LOVES THE LOVE OF TRUTH WE EASE OUR OWN INDOLENT CONSCIENCE BY CALLING HIM NAMES"
    expected = '<span>NOT HAVING THE COURAGE OR THE </span><del style="background:#ffe6e6;">INDUSTRY</del><ins style="background:#e6ffe6;">Bla</ins><span> OF OUR NEIGHBO</span><del style="background:#ffe6e6;">U</del><span>R WHO WORKS LIKE A BUSY BEE IN THE </span><del style="background:#ffe6e6;">WORLD </del><span>OF MEN AND BOOKS SEARCHING WITH THE SWEAT OF HIS BROW</span><ins style="background:#e6ffe6;"> some insertion</ins><span> FOR THE REAL BREAD OF LIFE WETTING THE OPEN PAGE BEFORE HIM WITH HIS TEARS PUSHING INTO THE WE HOURS OF THE NIGHT HIS QUEST ANIMATED BY THE FAIREST OF ALL LOVES THE LOVE OF TRUTH WE EASE OUR OWN INDOLENT CONSCIENCE BY CALLING HIM NAMES</span>'

    diff_html = diff_to_html_via_dmp(text, text2)
    assert diff_html == expected
    write_file("diff.html", diff_html)
