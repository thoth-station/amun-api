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

import logging

from thoth.common import OpenShift

from .configuration import Configuration

_LOGGER = logging.getLogger(__name__)


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

    response = openshift.ocp_client.resources.get(api_version='v1', kind=imagestream['kind']).create(
        body=imagestream,
        namespace=Configuration.AMUN_INSPECTION_NAMESPACE
    )

    response = response.to_dict()
    _LOGGER.debug("OpenShift response for creating Amun ImageStream: %r", response)

    return response['metadata']['name']


def create_inspect_buildconfig(openshift: OpenShift, inspection_id: str, dockerfile: str, specification: dict) -> None:
    """Create build config for the given image stream."""
    if 'hardware' in specification['build']['hardware']:
        response = openshift.ocp_client.resources.get(api_version='v1', kind='Template').get(
            namespace=Configuration.AMUN_INFRA_NAMESPACE,
            label_selector='template=amun-inspect-buildconfig-HW'
            )
    else:
        response = openshift.ocp_client.resources.get(api_version='v1', kind='Template').get(
            namespace=Configuration.AMUN_INFRA_NAMESPACE,
            label_selector='template=amun-inspect-buildconfig'
            )

    openshift._raise_on_invalid_response_size(response)
    response = response.to_dict()
    _LOGGER.debug("OpenShift response for getting Amun inspect BuildConfig template: %r", response)

    parameters = {
        'AMUN_INSPECTION_ID': inspection_id,
        'AMUN_GENERATED_DOCKERFILE': dockerfile
    }

    template = response['items'][0]

    if 'build' in specification:
        if 'requests' in specification['build']['requests']:
            build_specification = specification['build']['requests']
            if 'cpu' in build_specification['cpu']:
                parameters['AMUN_BUILD_CPU'] = build_specification['cpu']
            if 'memory' in build_specification['memory']:
                parameters['AMUN_BUILD_MEMORY'] = build_specification['memory']

        if 'hardware' in specification['build']['hardware']:
            hardware_specification = specification['build']['hardware']
            if 'cpu_family' in hardware_specification['cpu_family']:
                parameters['CPU_FAMILY'] = hardware_specification['cpu_family']
            if 'cpu_model' in hardware_specification['cpu_model']:
                parameters['CPU_MODEL'] = hardware_specification['cpu_model']
            if 'physical_cpus' in hardware_specification['physical_cpus']:
                parameters['PHYSICAL_CPUS'] = hardware_specification['physical_cpus']
            if 'processor' in hardware_specification['processor']:
                parameters['Processor'] = hardware_specification['processor']

    openshift.set_template_parameters(
        template,
        **parameters,
        )

    template = openshift.oc_process(Configuration.AMUN_INSPECTION_NAMESPACE, template)
    buildconfig = template['objects'][0]

    response = openshift.ocp_client.resources.get(api_version='v1', kind=buildconfig['kind']).create(
        body=buildconfig,
        namespace=Configuration.AMUN_INSPECTION_NAMESPACE
    )

    _LOGGER.debug("OpenShift response for creating Amun BuildConfig: %r", response.to_dict())


def create_inspect_job(openshift: OpenShift, image_stream_name: str, specification: dict) -> None:
    """Create the actual inspect job."""
    if 'hardware' in specification['run']['hardware']:
        response = openshift.ocp_client.resources.get(api_version='v1', kind='Template').get(
            namespace=Configuration.AMUN_INFRA_NAMESPACE,
            label_selector='template=amun-inspect-job-HW'
            )
    else:
        response = openshift.ocp_client.resources.get(api_version='v1', kind='Template').get(
            namespace=Configuration.AMUN_INFRA_NAMESPACE,
            label_selector='template=amun-inspect-job'
            )

    openshift._raise_on_invalid_response_size(response)
    response = response.to_dict()
    _LOGGER.debug("OpenShift response for getting Amun inspect Job template: %r", response)

    parameters = {
        'AMUN_INSPECTION_ID': image_stream_name
    }

    template = response['items'][0]

    if 'run' in specification:
        if 'requests' in specification['run']['requests']:
            run_specification = specification['run']['requests']
            if 'cpu' in run_specification['cpu']:
                parameters['AMUN_BUILD_CPU'] = run_specification['cpu']
            if 'memory' in run_specification['memory']:
                parameters['AMUN_BUILD_MEMORY'] = run_specification['memory']

        if 'hardware' in specification['run']['hardware']:
            hardware_specification = specification['run']['hardware']
            if 'cpu_family' in hardware_specification['cpu_family']:
                parameters['CPU_FAMILY'] = hardware_specification['cpu_family']
            if 'cpu_model' in hardware_specification['cpu_model']:
                parameters['CPU_MODEL'] = hardware_specification['cpu_model']
            if 'physical_cpus' in hardware_specification['physical_cpus']:
                parameters['PHYSICAL_CPUS'] = hardware_specification['physical_cpus']
            if 'processor' in hardware_specification['processor']:
                parameters['Processor'] = hardware_specification['processor']

    openshift.set_template_parameters(
        template,
        **parameters,
        )

    template = openshift.oc_process(Configuration.AMUN_INSPECTION_NAMESPACE, template)
    job = template['objects'][0]

    response = openshift.ocp_client.resources.get(api_version='v1', kind=job['kind']).create(
        body=job,
        namespace=Configuration.AMUN_INSPECTION_NAMESPACE
    )

    _LOGGER.debug("OpenShift response for creating Amun Job: %r", response.to_dict())
