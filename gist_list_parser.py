#!/usr/bin/env python3

import re
import subprocess
from collections import namedtuple
from datetime import datetime
from functools import partial
from io import StringIO
from pprint import pprint
from subprocess import PIPE, STDOUT
from typing import NamedTuple

class GistInfo(NamedTuple):

    hash : str
    file_count : int
    descr : str
    access : str
    last_update : datetime

    def __str__(self):
        return f"{self.last_update:%b %d, %Y %I:%M:%S %p} ({self.access}) " \
               f"{self.file_count}\n{self.hash:<32}\n" \
               f"{self.descr}\n"


GIST_RE : re.Pattern = re.compile(r"(?P<hash>[a-f0-9]+)\t"
                         r"(?P<descr>.*)\t" 
                         r"(?P<file_count>\d+\sfiles?)\t"
                         r"(?P<access>(public|secret))\t"
                         r"(?P<last_update>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")

def run_gh_command(limit:int=100) -> str:
    args : list[str] = f"gh gist list -L {limit}".split()
    cp = subprocess.run(args, stdout=PIPE, stderr=STDOUT, check=True, 
                        encoding="utf-8")
    return cp.stdout

def read_gist_list(filename: str) -> list[str]:
    with open(filename) as fp:
        return [line for line in fp.readlines()]

def parse_date_time_string(date_time_string: str) -> datetime:
    return datetime.strptime(date_time_string, "%Y-%m-%dT%H:%M:%SZ")

def parse_gist_line(line : str) -> GistInfo:
    m = GIST_RE.search(line)
    if m:
        return GistInfo(hash=m["hash"], 
                        file_count=m["file_count"],
                        access=m["access"],
                        descr=m["descr"],
                        last_update=parse_date_time_string(m["last_update"]))
    else:
        raise ValueError(f"The line\n\n{line}\n\ncould not be parsed.")

def get_info_last_update(info:GistInfo) -> datetime:
    return info.last_update

def sort_infos_asc(infos: list[GistInfo]) -> list[GistInfo]:
    return sorted(infos, key=get_info_last_update)

def get_info_list() -> list[GistInfo]:
    sp: StringIO
    with StringIO(run_gh_command()) as sp:
        lines : list[str] = sp.readlines()

    infos: list[GistInfo] = [parse_gist_line(line) for line in lines]
    return sort_infos_asc(infos)

def main() -> None:
    infos : list[GistInfo] = get_info_list() 

    info : GistInfo
    for info in infos:
         print(str(info))

if __name__ == "__main__":
    main()
