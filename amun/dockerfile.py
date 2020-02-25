#!/usr/bin/env python3
# Amun
# Copyright(C) 2018, 2019, 2020 Fridolin Pokorny
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

"""Utility functions for Amun API."""

import json
import logging
import os
import re

import toml
import requests

from functools import reduce

from .exceptions import ScriptObtainingError

_LOGGER = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENTRYPOINT_PY = os.path.join(_HERE, "inspect.py")
# Make sure pip and Pipenv trust the AICoE index.
_PIP_CONF = """
[global]
trusted-host = tensorflow.pypi.thoth-station.ninja
"""


def _determine_update_string() -> str:
    """Determine how to update the system to the latest version based on binaries present in the image."""
    return "RUN dnf update -y || yum update -y || apt-cache update"


def _determine_installer_string() -> str:
    """Determine how to install packages on the system regardless of package manager."""
    return (
        "RUN { \\\n\n"
        "  { [ -f '/usr/bin/dnf' ] && INSTALL_CMD='dnf install -y'; } || \\\n\n"
        "  { [ -f '/usr/bin/yum' ] && INSTALL_CMD='yum install -y'; } || \\\n\n"
        "  { INSTALL_CMD='apt-get install'; } \\\n\n"
        "}; eval $INSTALL_CMD "
    )


def _obtain_script(script: str) -> str:
    """Obtain script if it was specified by an URL, if script was provided inline, return it."""
    if script.startswith(("https://", "http://")):
        # Download script from remote if needed.
        response = requests.get(script)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise ScriptObtainingError(
                f"Failed to obtain script from {script} (HTTP status: {response.status_code})"
            )

        return response.text

    return script


def _write_file_string(content: str, path: str) -> str:
    """Generate Dockerfile instruction that writes down the file content on the given path."""
    # TODO: accept a list of files so we generate only one layer for all files
    # TODO: escape content
    # TODO: handle it in nice way so we can see it nicely in OpenShift's configuration
    content = content.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n\\\\n")
    path = path.replace('"', '"')
    return f'RUN echo -e "{content}" > "{path}"\n\n'


def create_dockerfile(specification: dict) -> tuple:
    """Create a Dockerfile based on software stack specification."""
    script_present = False
    dockerfile = "FROM " + specification["base"] + "\n\n"

    dockerfile += "USER root\n\n"

    env_str = ""
    for environ in specification.get("environment", []):
        env_str += f"{environ['name']}={environ['value']} "

    if env_str:
        dockerfile += f"ENV {env_str}\n\n"

    # Updating the base has to be turned on explicitly.
    if specification.get("update", False):
        dockerfile += _determine_update_string() + "\n\n"

    if specification.get("packages"):
        dockerfile += (
            _determine_installer_string() + " ".join(specification["packages"]) + "\n\n"
        )

    if specification.get("python_packages"):
        dockerfile += (
            "RUN pip3 install --force-reinstall --upgrade "
            + " ".join(specification["python_packages"])
            + "\n\n"
        )

    for file_spec in specification.get("files", []):
        path = file_spec["path"]
        content = file_spec["content"]
        # This trick helps so that env variables are not expanded.
        dockerfile += _write_file_string(content, path)

    # Create workdir only if needed.
    if "python" in specification or "script" in specification:
        dockerfile += f"RUN mkdir -p /home/amun && chmod -R 777 /home/amun\n\n"

    if "python" in specification:
        requirements = specification["python"]["requirements"]
        requirements_locked = specification["python"]["requirements_locked"]

        if not any([requirements, requirements_locked]):
            _LOGGER.debug("No requirements specified.")
        elif not all([requirements, requirements_locked]):
            raise ValueError(
                "Both `requirements` and `requirements_locked` must be provided."
            )
        else:
            pipfile_content = toml.dumps(requirements)
            dockerfile += _write_file_string(pipfile_content, "/home/amun/Pipfile")

            pipfile_lock_content = json.dumps(
                requirements_locked, sort_keys=True, indent=4
            )
            dockerfile += _write_file_string(
                pipfile_lock_content, "/home/amun/Pipfile.lock"
            )

            dockerfile += _write_file_string(_PIP_CONF, "/etc/pip.conf")

            if specification.get("package_manager", "micropipenv") == "micropipenv":
                dockerfile += "RUN cd /home/amun && " \
                              "python3 -m venv venv/ && " \
                              ". venv/bin/activate && " \
                              "micropipenv install --deploy\n\n"
            elif specification.get("package_manager") == "pipenv":
                dockerfile += "RUN cd /home/amun && pipenv install --deploy\n\n"
            else:
                raise ValueError(f"Unknown package manager to be used {specification.get('package_manager')!r}")

    if "script" in specification:
        script_present = True
        content = _obtain_script(specification["script"])
        dockerfile += _write_file_string(content, "/home/amun/script")
        with open(_ENTRYPOINT_PY, "r") as entrypoint_file:
            dockerfile += _write_file_string(
                entrypoint_file.read(), "/home/amun/entrypoint"
            )

        dockerfile += (
            "RUN chmod a+x /home/amun/script /home/amun/entrypoint && "
            "touch /home/amun/script.stderr /home/amun/script.stdout && "
            "chmod 777 /home/amun/script.stderr /home/amun/script.stdout\n\n"
        )
        dockerfile += 'CMD ["/home/amun/entrypoint"]\n\n'

    # An arbitrary user.
    dockerfile += "USER 1042\n\n"
    dockerfile += "WORKDIR /home/amun"

    return dockerfile, script_present
