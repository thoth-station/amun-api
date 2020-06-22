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

"""Implementation of API v1."""

import logging
import re
from typing import Any
from typing import Dict
from typing import Tuple

from thoth.common import OpenShift
from thoth.common import datetime2datetime_str
from thoth.common.exceptions import NotFoundException
from thoth.storages import InspectionStore
from thoth.storages.exceptions import NotFoundError as StorageNotFoundError

from .configuration import Configuration
from .dockerfile import create_dockerfile
from .exceptions import ScriptObtainingError

_LOGGER = logging.getLogger(__name__)

_OPENSHIFT = OpenShift()

# These are default requests for inspection builds and runs if not stated
# otherwise. We explicitly assign defaults to requests coming to API so that
# the specification always carries these values in inspection documents.
_DEFAULT_REQUESTS = {"cpu": "500m", "memory": "256Mi"}


def _construct_parameters_dict(specification: dict) -> tuple:
    """Construct parameters that should be passed to build or inspection job."""
    # Name of parameters are shared in build/job templates so parameters are constructed regardless build or job.
    parameters = {}
    use_hw_template = False
    if "hardware" in specification.get("requests", {}):
        hardware_specification = specification.get("requests", {}).get("hardware", {})
        use_hw_template = True

        if "cpu_family" in hardware_specification:
            parameters["CPU_FAMILY"] = hardware_specification["cpu_family"]

        if "cpu_model" in hardware_specification:
            parameters["CPU_MODEL"] = hardware_specification["cpu_model"]

        if "physical_cpus" in hardware_specification:
            parameters["PHYSICAL_CPUS"] = hardware_specification["physical_cpus"]

        if "processor" in hardware_specification:
            parameters["PROCESSOR"] = hardware_specification["processor"]

    return parameters, use_hw_template


def _do_create_dockerfile(specification: dict) -> tuple:
    """Wrap dockerfile generation and report back an error if any."""
    try:
        return create_dockerfile(specification)
    except ScriptObtainingError as exc:
        return None, str(exc)


def post_generate_dockerfile(specification: dict):
    """Generate Dockerfile out of software stack specification."""
    parameters = {"specification": specification}

    dockerfile, error = _do_create_dockerfile(specification)
    if dockerfile is None:
        return {"parameters": parameters, "error": error}, 400

    return {"parameters": parameters, "dockerfile": dockerfile}, 200


def _adjust_default_requests(dict_: dict) -> None:
    """Explicitly assign default requests so that they are carried within the requested inspection run."""
    if "requests" not in dict_:
        dict_["requests"] = {}

    dict_["requests"]["cpu"] = dict_["requests"].get("cpu") or _DEFAULT_REQUESTS["cpu"]
    dict_["requests"]["memory"] = dict_["requests"].get("memory") or _DEFAULT_REQUESTS["memory"]


def _parse_specification(specification: dict) -> dict:
    """Parse inspection specification.

    Cast types to comply with Argo and escapes quotes.
    """
    parsed_specification = specification.copy()

    def _escape_single_quotes(obj):
        if isinstance(obj, dict):
            for k in obj:
                obj[k] = _escape_single_quotes(obj[k])
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                obj[i] = _escape_single_quotes(v)
        elif isinstance(obj, str):
            return re.sub(r"'(?!')", "''", obj)

        return obj

    parsed_specification = _escape_single_quotes(parsed_specification)

    if "batch_size" in parsed_specification:
        parsed_specification["batch_size"] = str(specification["batch_size"])

    if "build" not in parsed_specification:
        parsed_specification["build"] = {}

    if "run" not in parsed_specification:
        parsed_specification["run"] = {}

    return parsed_specification


def _unparse_specification(parsed_specification: dict) -> dict:
    """Unparse inspection specification.

    Casts types to comply with the inspection scheme and unescapes quotes.
    """
    specification = parsed_specification.copy()

    def _unescape_single_quotes(obj):
        if isinstance(obj, dict):
            for k in obj:
                obj[k] = _unescape_single_quotes(obj[k])
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                obj[i] = _unescape_single_quotes(v)
        elif isinstance(obj, str):
            return re.sub(r"''", "'", obj)

        return obj

    specification = _unescape_single_quotes(specification)

    if "batch_size" in parsed_specification:
        parsed_specification["batch_size"] = int(parsed_specification["batch_size"])

    return specification


def get_version() -> Dict[str, Any]:
    """Obtain service version identifier."""
    from amun import __version__ as __amun_version__
    from amun.entrypoint import __version__ as __service_version__
    return {
        "version": __amun_version__,
        "service_version": __service_version__,
    }


def post_inspection(specification: dict) -> tuple:
    """Create new inspection for the given software stack."""
    # Generate first Dockerfile so we do not end up with an empty imagestream if Dockerfile creation fails.
    dockerfile, run_job_or_error = _do_create_dockerfile(specification)
    if dockerfile is None:
        return (
            {
                "parameters:": specification,
                # If not dockerfile is produced, run_job holds the error message.
                "error": run_job_or_error,
            },
            400,
        )

    run_job = run_job_or_error

    specification = _parse_specification(specification)

    _adjust_default_requests(specification["run"])
    _adjust_default_requests(specification["build"])

    parameters, use_hw_template = _construct_parameters_dict(specification.get("build", {}))

    # Mark this for later use - in get_inspection_specification().
    specification["@created"] = datetime2datetime_str()

    target = "inspection-run-result" if run_job else "inspection-build"

    dockerfile = dockerfile.replace("'", "''")

    inspection_id = _OPENSHIFT.schedule_inspection(
        dockerfile=dockerfile,
        specification=specification,
        target=target,
        parameters=parameters
    )

    # TODO: Check whether the workflow spec has been resolved successfully
    # The resolution happens on the server side, therefore even if the WF
    # is submitted successfully, it mail fail due to an invalid spec later on

    return (
        {
            "inspection_id": inspection_id,
            "parameters": specification,
        },
        202,
    )


def get_inspection_job_batch_size(inspection_id: str) -> Tuple[Dict[str, Any], int]:
    """Get batch size for the given inspection."""
    parameters = {"inspection_id": inspection_id}

    inspection_store = InspectionStore(inspection_id)
    inspection_store.connect()

    try:
        batch_size = inspection_store.results.get_results_count()
    except StorageNotFoundError:
        return {
            "error": f"No inspection {inspection_id!r} found",
            "parameters": parameters,
        }, 404

    return {"batch_size": batch_size, "parameters": parameters}, 200


def get_inspection_job_log(inspection_id: str, item: int) -> Tuple[Dict[str, Any], int]:
    """Get logs of the given inspection."""
    parameters = {"inspection_id": inspection_id}

    inspection_store = InspectionStore(inspection_id)
    inspection_store.connect()

    try:
        log = inspection_store.results.retrieve_log(item)
    except StorageNotFoundError:
        return {
            "error": f"No log for item {item!r} for inspection {inspection_id!r} or no "
                     f"inspection {inspection_id!r} with item {item} found",
            "parameters": parameters,
        }, 404

    return {"log": log, "parameters": parameters}, 200


def get_inspection_job_result(inspection_id: str, item: int) -> Tuple[Dict[str, Any], int]:
    """Get logs of the given inspection."""
    parameters = {"inspection_id": inspection_id}

    inspection_store = InspectionStore(inspection_id)
    inspection_store.connect()

    try:
        result = inspection_store.results.retrieve_result(item)
    except StorageNotFoundError:
        return {
            "error": f"No result for item {item!r} for inspection {inspection_id!r} or no "
                     f"inspection {inspection_id!r} with item {item} found",
            "parameters": parameters,
        }, 404

    return {"result": result, "parameters": parameters}, 200


def get_inspection_build_log(inspection_id: str) -> Tuple[Dict[str, Any], int]:
    """Get build log of an inspection."""
    parameters = {"inspection_id": inspection_id}

    inspection_store = InspectionStore(inspection_id)
    inspection_store.connect()

    try:
        log = inspection_store.builds.retrieve_log()
    except StorageNotFoundError:
        return {
            "error": "Build log for the given inspection id was not found",
            "parameters": parameters
        }, 404

    return {"log": log, "parameters": parameters}, 200


def get_inspection_specification(inspection_id: str) -> Tuple[Dict[str, Any], int]:
    """Get specification for the given build."""
    parameters = {"inspection_id": inspection_id}

    inspection_store = InspectionStore(inspection_id)
    inspection_store.connect()

    try:
        specification = inspection_store.retrieve_specification()
    except StorageNotFoundError:
        return {
            "error": f"No specification for inspection {inspection_id!r} found",
            "parameters": parameters,
        }, 404

    return {
        "parameters": parameters,
        "specification": specification,
    }, 200


def get_inspection_status(inspection_id: str) -> Tuple[Dict[str, Any], int]:
    """Get status of an inspection."""
    parameters = {"inspection_id": inspection_id}

    inspection_store = InspectionStore(inspection_id)
    inspection_store.connect()
    data_stored = inspection_store.exists()

    workflow_status = None
    try:
        wf: Dict[str, Any] = _OPENSHIFT.get_workflow(
            label_selector=f"inspection_id={inspection_id}", namespace=_OPENSHIFT.amun_inspection_namespace,
        )
        workflow_status = wf["status"]
    except NotFoundException:
        pass

    build_status = None
    try:
        # As we treat inspection_id same all over the places (dc, dc, job), we can
        # safely call gathering info about pod. There will be always only one build
        # (hopefully) - created per a user request.
        # OpenShift does not expose any endpoint for a build status anyway.
        build_status = _OPENSHIFT.get_pod_status_report(
            inspection_id + "-1-build", Configuration.AMUN_INSPECTION_NAMESPACE
        )
    except NotFoundException:
        pass

    return {
        "status": {
            "build": build_status,
            "data_stored": data_stored,
            "workflow": workflow_status
        },
        "parameters": parameters
    }, 200
