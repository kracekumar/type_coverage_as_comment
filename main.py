import os
from pathlib import Path
import click  # type: ignore
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup  # type: ignore
from typing import Optional
import re


@dataclass
class FileSummary:
    full_filename: str
    imprecision: float
    lines: int


@dataclass
class RunSummary:
    imprecision: float
    lines: int


@dataclass
class Result:
    run_summary: RunSummary
    file_summaries: list[FileSummary]


INT_REGEX = "[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"

class ClassName:
    FILENAME = 'summary-filename'
    IMPRECISION = 'summary-precision'
    LINES = 'summary-lines'


def get_type_coverage(cov_filename: Path) -> Result:
    with open(cov_filename) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    run_summary: RunSummary = None  # type: ignore
    file_summaries: list[FileSummary] = []

    for tr in soup.table.find_all('tr'):
        # Get all the file summaries
        full_filename, imprecision, lines, top_level_module = '', 0.00, 0, ''
        for td in tr.find_all('td'):
            val = td.get_text()
            classes = td.get('class')
            if ClassName.FILENAME in classes:
                full_filename = val

            elif ClassName.IMPRECISION in classes:
                vals = re.findall(INT_REGEX, val)
                if vals:
                    imprecision = float(vals[0])

            elif ClassName.LINES in classes:
                vals = re.findall(INT_REGEX, val)
                if vals:
                    lines = vals[0]

        if full_filename:
            file_summaries.append(FileSummary(full_filename=full_filename,
                                              imprecision=imprecision,
                                              lines=lines))
    # Get the run summary

    for tfoot in soup.table.find_all('tfoot'):
        imprecision, lines = 0.0, 0
        for th in tfoot.find_all('th'):
            val = th.get_text()
            classes = th.get('class')
            if ClassName.IMPRECISION in classes:
                vals = re.findall(INT_REGEX, val)
                if vals:
                    imprecision = float(vals[0])

            elif ClassName.LINES in classes:
                vals = re.findall(INT_REGEX, val)
                if vals:
                    lines = vals[0]

        run_summary = RunSummary(imprecision=imprecision, lines=lines)

    return Result(run_summary=run_summary,
                  file_summaries=file_summaries)



def is_valid_path(html_report) -> bool:
    path = Path(html_report)
    return path.exists()


def validate_filepath(html_report: str) -> Path:
    if html_report:
        if is_valid_path(html_report):
            return Path(html_report)

    print(os.environ)
    html_report_env = os.environ.get('HTML_REPORT') or os.environ.get('html_report')
    print(list(Path(html_report_env).iterdir()))
    if html_report_env:
        if is_valid_path(html_report_env):
            return Path(html_report_env)
        raise ValueError(f'Unable to find {html_report_env} to parse.')

    raise ValueError('html_report path should be passed an argument or set as environment variable')


def find_modified_files():
    for key in ["GITHUB_WORKFLOW", "GITHUB_RUN_ID",
                "GITHUB_RUN_NUMBER", "GITHUB_REPOSITORY",
                "GITHUB_REF", "GITHUB_BASE_REF", ""]:
        print(key, os.environ.get(key))


@click.command()
@click.option("--html-report", type=str, default="")
def main(html_report: str):
    try:
        filepath = validate_filepath(html_report)
        type_result = get_type_coverage(filepath)
        print(find_modified_files())
    except Exception as exc:
        print(exc)


if __name__ == "__main__":
    main()
