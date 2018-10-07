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

"""Core Amun API configuration and entrypoint."""

import os
import sys
import logging

from flask import redirect
from flask import jsonify
import connexion
from flask_script import Manager
from thoth.common import datetime2datetime_str
#from thoth.common import init_logging
from datetime import datetime

from .configuration import Configuration

# TODO: enable once new thoth-common will be released with configurable prefix support
#init_logging()

# Expose for uWSGI.
app = connexion.App(__name__)
application = app.app
_LOGGER = logging.getLogger('amun')
_LOGGER.setLevel(logging.DEBUG if bool(int(os.getenv('AMUN_DEBUG', 0))) else logging.INFO)

app.add_api(Configuration.SWAGGER_YAML_PATH)
manager = Manager(application)
# Needed for session.
application.secret_key = Configuration.APP_SECRET_KEY


@app.route('/')
def base_url():
    """Redirect to UI by default."""
    return redirect('api/v1/ui')


@app.route('/api/v1')
def api_v1():
    """Provide a listing of all available endpoints."""
    paths = []

    for rule in application.url_map.iter_rules():
        rule = str(rule)
        if rule.startswith('/api/v1'):
            paths.append(rule)

    return jsonify({'paths': paths})


def _healthiness():
    return jsonify({
        'status': 'ready',
    }), 200, {'ContentType': 'application/json'}


@app.route('/readiness')
def api_readiness():
    """Report readiness for OpenShift readiness probe."""
    return _healthiness()


@app.route('/liveness')
def api_liveness():
    """Report liveness for OpenShift readiness probe."""
    return _healthiness()


@application.errorhandler(404)
def page_not_found(exc):
    """Adjust 404 page to be consistent with errors reported back from API."""
    # Flask has a nice error message - reuse it.
    return jsonify({'error': str(exc)}), 404


@application.errorhandler(500)
def internal_server_error(exc):
    """Adjust 500 page to be consistent with errors reported back from API."""
    # Provide some additional information so we can easily find exceptions in logs (time and exception type).
    # Later we should remove exception type (for security reasons).
    return jsonify({
        'error': 'Internal server error occurred, please contact administrator with provided details.',
        'details': {
            'type': exc.__class__.__name__,
            'datetime': datetime2datetime_str(datetime.utcnow())
        }
    }), 500


if __name__ == '__main__':
    sys.exit(1)
