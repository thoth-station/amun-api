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
initcontainer aggregating hardware information.
"""

import json
import sys
import subprocess
import hashlib
import sys


# A path to file containing hardware information as gathered by initcontainer
# amun-hwinfo.
_HWINFO_FILE = '/home/amun/hwinfo/info.json'
# We use a file for stdout and stderr not to block on pipe.
_EXEC_STDOUT_FILE = '/home/amun/script.stdout'
_EXEC_STDERR_FILE = '/home/amun/script.stderr'
# Executable to be run.
_EXEC_FILE = '/home/amun/script'


def main():
    """Entrypoint for inspection container."""
    # Load hardware info.
    with open(_HWINFO_FILE, 'r') as hwinfo_file:
        hwinfo = json.load(hwinfo_file)

    # Execute the supplied script.
    args = [_EXEC_FILE]
    with open(_EXEC_STDOUT_FILE, 'w') as stdout_file, open(_EXEC_STDERR_FILE) as stderr_file:
        process = subprocess.Popen(args, stdout=stdout_file, stderr=stderr_file, universal_newlines=True)
        process.wait()

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

    # Name return code as exit_code to be consistent in Thoht.
    report = {
        'hwinfo': hwinfo,
        'stdout': stdout,
        'stderr': stderr,
        'exit_code': process.returncode,
        'script_sha256': sha256.hexdigest()
    }

    json.dump(report, sys.stdout, sort_keys=True, indent=2)
    sys.exit(report['exit_code'])


if __name__ == '__main__':
    main()
