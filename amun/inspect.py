#!/usr/bin/env python3
# Amun
# Copyright(C) 2018, 2019 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""This file is run by an inspection pod to gather runtime information.

This script should not use any external libraries except for Python's standard
library. It acts as wrapper around user supplied script and prints command
results to stdout as a JSON. It also aggregates information from hwinfo
init-container aggregating hardware information.
"""

import os
import resource
import json
import subprocess
import hashlib
import sys
from datetime import datetime


# A path to file containing hardware information as gathered by init-container
# amun-hwinfo.
_HWINFO_FILE = "/home/amun/hwinfo/info.json"
# We use a file for stdout and stderr not to block on pipe.
_EXEC_STDOUT_FILE = "/home/amun/script.stdout"
_EXEC_STDERR_FILE = "/home/amun/script.stderr"
# Executable to be run.
_EXEC_FILE = "/home/amun/script"
# Names of items on certain position in return value of resource.getrusage()
#   https://docs.python.org/3.6/library/resource.html#resource.getrusage
_RESOURCE_STRUCT_RUSAGE_ITEMS = (
    "ru_utime",
    "ru_stime",
    "ru_maxrss",
    "ru_ixrss",
    "ru_idrss",
    "ru_isrss",
    "ru_minflt",
    "ru_majflt",
    "ru_nswap",
    "ru_inblock",
    "ru_oublock",
    "ru_msgsnd",
    "ru_msgrcv",
    "ru_nsignals",
    "ru_nvcsw",
    "ru_nivcsw",
)


def main():
    """Entrypoint for inspection container."""
    # Load hardware info.
    hwinfo = None
    with open(_HWINFO_FILE, "r") as hwinfo_file:
        hwinfo = json.load(hwinfo_file)

    # Execute the supplied script.
    args = ["pipenv", "run", _EXEC_FILE]
    with open(_EXEC_STDOUT_FILE, "w") as stdout_file, open(_EXEC_STDERR_FILE, "w") as stderr_file:
        process = subprocess.Popen(args, stdout=stdout_file, stderr=stderr_file, universal_newlines=True)

    process.communicate()

    usage_info = resource.getrusage(resource.RUSAGE_CHILDREN)

    usage = {}
    for idx in range(len(_RESOURCE_STRUCT_RUSAGE_ITEMS)):
        usage[_RESOURCE_STRUCT_RUSAGE_ITEMS[idx]] = usage_info[idx]

    # Load stdout and stderr.
    with open(_EXEC_STDOUT_FILE, "r") as stdout_file:
        stdout = stdout_file.read()
        try:
            stdout = json.loads(str(stdout))
        except Exception:
            # We were not able to load JSON, pass string as output.
            pass

    with open(_EXEC_STDERR_FILE, "r") as stderr_file:
        stderr = stderr_file.read()

    # Compute script SHA-256.
    sha256 = hashlib.sha256()
    with open(_EXEC_FILE, "rb") as script_file:
        while True:
            data = script_file.read(65536)
            if not data:
                break

            sha256.update(data)

    # Name return code as exit_code to be consistent in Thoth.
    report = {
        "hwinfo": hwinfo,
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": process.returncode,
        "script_sha256": sha256.hexdigest(),
        "usage": usage_info,
        "datetime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f"),
    }

    json.dump(report, sys.stdout, sort_keys=True, indent=2)
    sys.exit(report["exit_code"])


if __name__ == "__main__":
    main()
