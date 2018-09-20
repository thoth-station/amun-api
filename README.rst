Amun Service
------------

Installation and Deployment
===========================

.. code-block:: console

  # Adjust configuration in the provision.yaml file.
  vim playbooks/provision.yaml
  # Deploy to the OpenShift cluster.
  oc login https://...
  OCP_URL=$(oc whoami --show-server) OCP_TOKEN=$(oc whoami --show-token) ansible-playbook playbooks/provision.yaml
