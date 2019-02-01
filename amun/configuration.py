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

"""Configuration of Amun API service."""

import os


class Configuration:
    """Configuration of Amun API service."""

    APP_SECRET_KEY = os.environ['AMUN_API_APP_SECRET_KEY']
    SWAGGER_YAML_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'swagger.yaml')
    AMUN_INSPECTION_NAMESPACE = os.environ['THOTH_AMUN_INSPECTION_NAMESPACE']
    AMUN_INFRA_NAMESPACE = os.environ['THOTH_AMUN_INFRA_NAMESPACE']
