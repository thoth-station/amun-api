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

"""Implementation of API v1."""

import logging
import random

from thoth.common import OpenShift
from thoth.common.exceptions import NotFoundException

from .configuration import Configuration
from .core import create_inspect_buildconfig
from .core import create_inspect_imagestream
from .core import create_inspect_job
from .dockerfile import create_dockerfile
from .exceptions import ScriptObtainingError

_LOGGER = logging.getLogger('amun.api_v1')
_OPENSHIFT = OpenShift()


def _do_create_dockerfile(specification: dict) -> tuple:
    """Wrap dockerfile generation and report back an error if any."""
    try:
        return create_dockerfile(specification)
    except ScriptObtainingError as exc:
        return None, str(exc)


def _generate_inspection_id():
    """Generate a random identifier for the given inspection."""
    # A very first method used 'generatedName' in ImageStream configuration,
    # but it looks like there is a bug in OpenShift as it did not generated any
    # name and failed with regexp issues (that were not related to the
    # generateName configuration).
    return 'inspect-' + "%016x" % random.getrandbits(64)


def post_generate_dockerfile(specification: dict):
    """Generate Dockerfile out of software stack specification."""
    dockerfile, error = _do_create_dockerfile(specification)
    if dockerfile is None:
        return {
            'parameters': specification,
            'error': error
        }, 400

    return {
        'parameters': specification,
        'dockefile': dockerfile
    }, 200


def post_inspection(specification: dict) -> dict:
    """Create new inspection for the given software stack."""
    # Generate first Dockerfile so we do not end up with an empty imagestream if Dockerfile creation fails.
    dockerfile, run_job = _do_create_dockerfile(specification)
    if dockerfile is None:
        return {
            'parameters:': specification,
            # If not dockerfile is produced, run_job holds the error message.
            'error': run_job
        }, 400

    inspection_id = _generate_inspection_id()
    create_inspect_imagestream(_OPENSHIFT, inspection_id)
    create_inspect_buildconfig(_OPENSHIFT, inspection_id, dockerfile)

    if run_job:
        create_inspect_job(_OPENSHIFT, inspection_id)

    return {
        'parameters': specification,
        'inspection_id': inspection_id,
        'job_created': run_job,
        'build_created': True
    }, 202


def get_inspection_job_log(inspection_id: str) -> dict:
    """Get logs of the given inspection."""
    parameters = {'inspection_id': inspection_id}
    try:
        log = _OPENSHIFT.get_job_log(inspection_id, Configuration.AMUN_INSPECTION_NAMESPACE)
    except NotFoundException:
        return {
            'error': 'Job log for the given inspection id was not found',
            'parameters': parameters
        }, 404

    return {
        'log': log,
        'parameters': parameters
    }, 200


def get_inspection_build_log(inspection_id: str) -> dict:
    """Get build log of an inspection."""
    parameters = {'inspection_id': inspection_id}

    try:
        status = _OPENSHIFT.get_pod_log(
            inspection_id + '-1-build',
            Configuration.AMUN_INSPECTION_NAMESPACE
        )
    except NotFoundException:
        return {
            'error': 'Build log with for the given inspection id was not found',
            'parameters': parameters
        }, 404

    return {
        'status': status,
        'parameters': parameters
    }, 200


def get_inspection_status(inspection_id: str) -> dict:
    """Get status of an inspection."""
    parameters = {'inspection_id': inspection_id}

    build_status = None
    try:
        # As we treat inspection_id same all over the places (dc, dc, job), we can
        # safely call gathering info about pod. There will be always only one build
        # (hopefully) - created per a user request.
        # OpenShift does not expose any endpoint for a build status anyway.
        build_status = _OPENSHIFT.get_pod_status_report(
            inspection_id + '-1-build',
            Configuration.AMUN_INSPECTION_NAMESPACE
        )
    except NotFoundException:
        return {
            'error': 'The given inspection id was not found',
            'parameters': parameters
        }, 404

    job_status = None
    try:
        job_status = _OPENSHIFT.get_job_status_report(
            inspection_id,
            Configuration.AMUN_INSPECTION_NAMESPACE
        )
    except NotFoundException:
        # There was no job scheduled - user did not submitted any script to run the job. Report None.
        pass

    return {
        'build': build_status,
        'job': job_status,
        'parameters': parameters
    }, 200
