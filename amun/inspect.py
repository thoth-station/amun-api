#!/usr/bin/env python3
# Amun
# Copyright(C) 2018 Fridolin Pokorny
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

This script should not use any extern libraries except for Python's standard
library. It acts as an wrapper around user supplied script and prints command
results to stdout as a JSON. It also aggregates information from hwinfo
init-container aggregating hardware information.
"""

import os
import json
import subprocess
import hashlib
import sys
import time


# A path to file containing hardware information as gathered by init-container
# amun-hwinfo.
_HWINFO_FILE = '/home/amun/hwinfo/info.json'
# We use a file for stdout and stderr not to block on pipe.
_EXEC_STDOUT_FILE = '/home/amun/script.stdout'
_EXEC_STDERR_FILE = '/home/amun/script.stderr'
# Executable to be run.
_EXEC_FILE = '/home/amun/script'

_G_PROCESS = None
_G_CPU_STATS = None


def sig_handler(signal_number, _):
    """Handle SIGCHLD on sub-process when it is in zombie mode to gather CPU statistics."""
    global _G_PROCESS
    global _G_CPU_STATS

    with open(f"/proc/{_G_PROCESS.pid}/stat") as stat_file:
        values = stat_file.readline().split()

    # Refer to:
    #   http://man7.org/linux/man-pages/man5/proc.5.html
    clock_ticks = os.sysconf("SC_CLK_TCK")
    utime = float(values[13]) / clock_ticks
    stime = float(values[14]) / clock_ticks
    cutime = float(values[15]) / clock_ticks
    cstime = float(values[16]) / clock_ticks
    total_time = utime + stime

    _G_CPU_STATS = {
        "utime": utime,
        "stime": stime,
        "cutime": cutime,
        "cstime": cstime,
        "total_time": total_time
    }


def main():
    """Entrypoint for inspection container."""
    # Load hardware info.
    global _G_PROCESS
    global _G_CPU_STATS

    with open(_HWINFO_FILE, 'r') as hwinfo_file:
        hwinfo = json.load(hwinfo_file)

    # Execute the supplied script.
    args = ['pipenv', 'run', _EXEC_FILE]
    with open(_EXEC_STDOUT_FILE, 'w') as stdout_file, open(_EXEC_STDERR_FILE, 'w') as stderr_file:
        _G_PROCESS = subprocess.Popen(args, stdout=stdout_file, stderr=stderr_file, universal_newlines=True)

    # Wait for process to finish. We need to do it actively from Python interpreter and
    # cannot use os.waitpid() due to SIGCHLD handler.
    while _G_PROCESS.poll() is None:
        time.sleep(0.1)

    # Load stdout and stderr.
    with open(_EXEC_STDOUT_FILE, 'r') as stdout_file:
        stdout = stdout_file.read()
        try:
            stdout = json.loads(str(stdout))
        except Exception:
            # We were not able to load JSON, pass string as output.
            pass

    with open(_EXEC_STDERR_FILE, 'r') as stderr_file:
        stderr = stderr_file.read()

    # Compute script SHA-256.
    sha256 = hashlib.sha256()
    with open(_EXEC_FILE, 'rb') as script_file:
        while True:
            data = script_file.read(65536)
            if not data:
                break

            sha256.update(data)

    # Name return code as exit_code to be consistent in Thoth.
    report = {
        'hwinfo': hwinfo,
        'stdout': stdout,
        'stderr': stderr,
        'exit_code': _G_PROCESS.returncode,
        'script_sha256': sha256.hexdigest(),
        'cpu': _G_CPU_STATS
    }

    json.dump(report, sys.stdout, sort_keys=True, indent=2)
    sys.exit(report['exit_code'])


if __name__ == '__main__':
    main()
