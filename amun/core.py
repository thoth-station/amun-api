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

"""Core parts of Amun for spawning builds and inspect runs."""

import json
import logging

from thoth.common import OpenShift

from .configuration import Configuration

_LOGGER = logging.getLogger(__name__)


def _construct_parameters_dict(specificaiton: dict) -> dict:
    """Construct parameters that should be passed to build or inspection job."""
    # Name of parameters are shared in build/job templates so parameters are constructed regardless build or job.
    parameters = {}
    use_hw_template = False

    if 'cpu' in specification['requests']:
        parameters['AMUN_CPU'] = specification['requests']['cpu']
    if 'memory' in specification:
        parameters['AMUN_MEMORY'] = specification['requests']['memory']

    if 'hardware' in specification['requests']:
        hardware_specification = specification['requests']['hardware']
        use_hw_template = True

        if 'cpu_family' in hardware_specification:
            parameters['CPU_FAMILY'] = hardware_specification['cpu_family']

        if 'cpu_model' in hardware_specification:
            parameters['CPU_MODEL'] = hardware_specificaiton['cpu_model']

        if 'physical_cpus' in hardware_specification:
            parameters['PHYSICAL_CPUS'] = hardware_specificaiton['physical_cpus']

        if 'processor' in hardware_specification:
            parameters['PROCESSOR'] = hardware_specification['processor']

    return parameters, use_hw_template


def create_inspect_imagestream(openshift: OpenShift, inspection_id: str) -> str:
    """Dynamically create imagestream on user request."""
    response = openshift.ocp_client.resources.get(api_version='v1', kind='Template').get(
        namespace=Configuration.AMUN_INFRA_NAMESPACE,
        label_selector='template=amun-inspect-imagestream'
    )

    openshift._raise_on_invalid_response_size(response)

    response = response.to_dict()
    _LOGGER.debug("OpenShift response for getting Amun inspect ImageStream template: %r", response)
    template = response['items'][0]

    openshift.set_template_parameters(template, AMUN_INSPECTION_ID=inspection_id)
    template = openshift.oc_process(Configuration.AMUN_INSPECTION_NAMESPACE, template)
    imagestream = template['objects'][0]

    response = openshift.ocp_client.resources.get(
        api_version=imagestream['apiVersion'],
        kind=imagestream['kind']
    ).create(
        body=imagestream,
        namespace=Configuration.AMUN_INSPECTION_NAMESPACE
    )

    response = response.to_dict()
    _LOGGER.debug("OpenShift response for creating Amun ImageStream: %r", response)

    return response['metadata']['name']


def create_inspect_buildconfig(openshift: OpenShift, inspection_id: str, dockerfile: str, specification: dict) -> None:
    """Create build config for the given image stream."""
    parameters, use_hw_template = _construct_parameters_dict(specification['build'])
    parameters['AMUN_INSPECTION_ID'] = inspection_id,
    parameters['AMUN_GENERATED_DOCKERFILE'] = dockerfile,
    parameters['AMUN_SPECIFICATION'] json.dumps(specification)

    if use_hw_template:
        label_selector = 'template=amun-inspect-buildconfig-cpu-hw'
    else:
        label_selector = 'template=amun-inspect-buildconfig'

    response = openshift.ocp_client.resources.get(api_version='v1', kind='Template').get(
        namespace=Configuration.AMUN_INFRA_NAMESPACE,
        label_selector=label_selector
    )

    openshift._raise_on_invalid_response_size(response)
    response = response.to_dict()
    _LOGGER.debug("OpenShift response for getting Amun inspect BuildConfig template: %r", response)

    template = response['items'][0]

    openshift.set_template_parameters(
        template,
        **parameters,
    )

    template = openshift.oc_process(Configuration.AMUN_INSPECTION_NAMESPACE, template)
    buildconfig = template['objects'][0]

    response = openshift.ocp_client.resources.get(
        api_version=buildconfig['apiVersion'],
        kind=buildconfig['kind']
    ).create(
        body=buildconfig,
        namespace=Configuration.AMUN_INSPECTION_NAMESPACE
    )

    _LOGGER.debug("OpenShift response for creating Amun BuildConfig: %r", response.to_dict())


def create_inspect_job(openshift: OpenShift, image_stream_name: str, specification: dict) -> None:
    """Create the actual inspect job."""
    parameters, use_hw_template = _construct_parameters_dict(specification['run'])
    parameters['AMUN_INSPECTION_ID'] = image_stream_name

    if use_hw_template:
        label_selector = 'template=amun-inspect-job-cpu-hw'
    else:
        label_selector = 'template=amun-inspect-job'

    response = openshift.ocp_client.resources.get(api_version='v1', kind='Template').get(
        namespace=Configuration.AMUN_INFRA_NAMESPACE,
        label_selector=label_selector
    )

    openshift._raise_on_invalid_response_size(response)
    response = response.to_dict()
    _LOGGER.debug("OpenShift response for getting Amun inspect Job template: %r", response)

    template = response['items'][0]

    openshift.set_template_parameters(
        template,
        **parameters,
    )

    template = openshift.oc_process(Configuration.AMUN_INSPECTION_NAMESPACE, template)
    job = template['objects'][0]

    response = openshift.ocp_client.resources.get(
        api_version=job['apiVersion'],
        kind=job['kind']
    ).create(
        body=job,
        namespace=Configuration.AMUN_INSPECTION_NAMESPACE
    )

    _LOGGER.debug("OpenShift response for creating Amun Job: %r", response.to_dict())
