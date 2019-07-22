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

"""Implementation of API v1."""

import logging
import random
import json

from thoth.common import OpenShift
from thoth.common import datetime2datetime_str
from thoth.common.exceptions import NotFoundException

from .configuration import Configuration
from .dockerfile import create_dockerfile
from .exceptions import ScriptObtainingError

_LOGGER = logging.getLogger(__name__)
_OPENSHIFT = OpenShift()

# These are default requests for inspection builds and runs if not stated
# otherwise. We explicitly assign defaults to requests coming to API so that
# the specification always carries these values in inspection documents.
_DEFAULT_REQUESTS = {
    "cpu": "500m",
    "memory": "256Mi"
}


def _construct_parameters_dict(specification: dict) -> tuple:
    """Construct parameters that should be passed to build or inspection job."""
    # Name of parameters are shared in build/job templates so parameters are constructed regardless build or job.
    parameters = {}
    use_hw_template = False
    if 'hardware' in specification.get('requests', {}):
        hardware_specification = specification.get('requests', {}).get('hardware', {})
        use_hw_template = True

        if 'cpu_family' in hardware_specification:
            parameters['CPU_FAMILY'] = hardware_specification['cpu_family']

        if 'cpu_model' in hardware_specification:
            parameters['CPU_MODEL'] = hardware_specification['cpu_model']

        if 'physical_cpus' in hardware_specification:
            parameters['PHYSICAL_CPUS'] = hardware_specification['physical_cpus']

        if 'processor' in hardware_specification:
            parameters['PROCESSOR'] = hardware_specification['processor']

    return parameters, use_hw_template


def _do_create_dockerfile(specification: dict) -> tuple:
    """Wrap dockerfile generation and report back an error if any."""
    try:
        return create_dockerfile(specification)
    except ScriptObtainingError as exc:
        return None, str(exc)


def _generate_inspection_id(identifier: str = None) -> str:
    """Generate a random identifier for the given inspection."""
    # A very first method used 'generatedName' in ImageStream configuration,
    # but it looks like there is a bug in OpenShift as it did not generated any
    # name and failed with regexp issues (that were not related to the
    # generateName configuration).
    if not identifier:
        return "inspection-" + "%016x" % random.getrandbits(64)

    return ("inspection-%s-" + "%016x") % (identifier, random.getrandbits(64))


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


def _adjust_default_requests(dict_: dict) -> None:
    """Explicitly assign default requests so that they are carried within the requested inspection run."""
    new_requests = dict(_DEFAULT_REQUESTS)
    requests = dict_.get('requests', {})
    new_requests.update(requests)
    dict_['requests'] = new_requests


def post_inspection(specification: dict) -> tuple:
    """Create new inspection for the given software stack."""
    # Generate first Dockerfile so we do not end up with an empty imagestream if Dockerfile creation fails.
    dockerfile, run_job = _do_create_dockerfile(specification)
    if dockerfile is None:
        return {
            'parameters:': specification,
            # If not dockerfile is produced, run_job holds the error message.
            'error': run_job
        }, 400

    if 'build' not in specification:
        specification['build'] = {}

    if 'run' not in specification:
        specification['run'] = {}

    _adjust_default_requests(specification['run'])
    _adjust_default_requests(specification['build'])

    inspection_id = _generate_inspection_id(specification.get("identifier"))
    _OPENSHIFT.create_inspection_imagestream(inspection_id)

    parameters, use_hw_template = _construct_parameters_dict(specification.get('build', {}))

    run_cpu_requests = None
    if 'cpu' in specification['run'].get('requests', {}):
        run_cpu_requests = specification['run']['requests']['cpu']

    run_memory_requests = None
    if 'memory' in specification['run'].get('requests', {}):
        run_memory_requests = specification['run']['requests']['memory']

    parameters['AMUN_INSPECTION_ID'] = inspection_id
    # Mark this for later use - in get_inspection_specification().
    specification["@created"] = datetime2datetime_str()

    # Create buildconfig, extend parameters with specification and generated dockerfile for build.
    build_parameters = dict(parameters)
    build_parameters['AMUN_GENERATED_DOCKERFILE'] = dockerfile
    build_parameters['AMUN_SPECIFICATION'] = json.dumps(specification)
    build_parameters['AMUN_CPU'] = specification['build'].get('requests', {}).get('cpu')
    build_parameters['AMUN_MEMORY'] = specification['build'].get('requests', {}).get('memory')
    _OPENSHIFT.schedule_inspection_build(build_parameters, inspection_id, use_hw_template)

    if run_job:
        _OPENSHIFT.schedule_inspection_job(
            inspection_id,
            parameters,
            use_hw_template=use_hw_template,
            memory_requests=run_memory_requests,
            cpu_requests=run_cpu_requests
        )

    return {
        'parameters': specification,
        'inspection_id': inspection_id,
        'job_created': run_job,
        'build_created': True
    }, 202


def get_inspection_job_log(inspection_id: str) -> tuple:
    """Get logs of the given inspection."""
    parameters = {'inspection_id': inspection_id}
    try:
        log = _OPENSHIFT.get_job_log(inspection_id, Configuration.AMUN_INSPECTION_NAMESPACE)
    except NotFoundException as exc:
        try:
            # Try to get status so a user knows to ask later.
            _OPENSHIFT.get_job_status_report(
                inspection_id,
                Configuration.AMUN_INSPECTION_NAMESPACE
            )
            return {
                'error': 'No logs available yet for the given inspection id',
                'parameters': parameters
            }, 202
        except NotFoundException:
            pass

        return {
            'error': 'Job log for the given inspection id was not found',
            'parameters': parameters
        }, 404

    if not log:
        return {
            'error': 'Inspection run did not produce any log or it was deleted by OpenShift',
            'parameters': parameters,
        }, 404

    try:
        log = json.loads(log)
    except Exception as exc:
        _LOGGER.exception("Failed to load inspection job log for %r", inspection_id)
        return {
            'error': 'Job failed, please contact administrator for more details',
            'parameters': parameters
        }, 500

    return {
        'log': log,
        'parameters': parameters
    }, 200


def get_inspection_build_log(inspection_id: str) -> tuple:
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
        'log': status,
        'parameters': parameters
    }, 200


def get_inspection_status(inspection_id: str) -> tuple:
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


def get_inspection_specification(inspection_id: str):
    """Get specification for the given build."""
    parameters = {'inspection_id': inspection_id}

    try:
        build = _OPENSHIFT.get_buildconfig(
            inspection_id,
            Configuration.AMUN_INSPECTION_NAMESPACE
        )
    except NotFoundException:
        return {
            'error': 'The given inspection id build was not found',
            'parameters': parameters
        }

    specification = json.loads(build['metadata']['annotations']['amun_specification'])
    # We inserted created information on our own, pop it not to taint the original specification request.
    created = specification.pop("@created")
    return {
        'parameters': parameters,
        'specification': specification,
        'created': created,
    }
