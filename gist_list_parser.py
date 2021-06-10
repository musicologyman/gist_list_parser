import re
import subprocess
from collections import namedtuple
from datetime import datetime
from functools import partial
from io import StringIO
from pprint import pprint
from subprocess import PIPE, STDOUT

GIST_RE = re.compile(r"(?P<hash>[a-f0-9]+)\t"
                     r"(?P<descr>.*)\t" 
                     r"(?P<file_count>\d+\sfiles?)\t"
                     r"(?P<access>(public|secret))\t"
                     r"(?P<last_update>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")


def run_gh_command(limit=100):
    args = f"gh gist list -L {limit}".split()
    cp = subprocess.run(args, stdout=PIPE, stderr=STDOUT, check=True, 
                        encoding="utf-8")
    return cp.stdout


def read_gist_list(filename):
    with open(filename) as fp:
        return [line for line in fp.readlines()]

def parse_date_time_string(date_time_string):
    return datetime.strptime(date_time_string, "%Y-%m-%dT%H:%M:%SZ")

GistInfo = namedtuple("GistInfo", "hash file_count descr access last_update")

def GistInfo_str(self):
    return f"{self.last_update:%b %d, %Y %I:%M:%S %p} ({self.access}) " \
           f"{self.file_count}\n{self.hash:<32}\n" \
           f"{self.descr}\n"

GistInfo.__str__ = GistInfo_str
    
def parse_gist_line(line):
    m = GIST_RE.search(line)
    if m:
        return GistInfo(hash=m["hash"], 
                        file_count=m["file_count"],
                        access=m["access"],
                        descr=m["descr"],
                        last_update=parse_date_time_string(m["last_update"]))
    else:
        raise ValueError(f"The line\n\n{line}\n\ncould not be parsed.")

def sort_infos_asc(infos):
    return sorted(infos, key=lambda info: info.last_update)

def main():
#    lines = read_gist_list("gist_list.txt")
    with StringIO(run_gh_command()) as sp:
        lines = sp.readlines()

    infos = [parse_gist_line(line) for line in lines]
    sorted_infos = sort_infos_asc(infos)
#    pprint(sorted_infos)
    for info in sorted_infos:
         print(str(info))

if __name__ == "__main__":
    main()




