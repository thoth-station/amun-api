Amun Service
------------

See `this blog post for a detailed walkthrough together with a video
demonstrating usage <https://towardsdatascience.com/how-to-beat-pythons-pip-inspecting-the-quality-of-machine-learning-software-f1a028f0c42a>`_.

Amun is a service that executes the given application stack in the requested
environment - given the list of package that should be installed as well as
given the hardware that is requested to run the application. Its primary
purpose is to act as an execution engine for Thoth where applications are
built and tested (applications are automatically generated given the software
requirements). However, it can be used to verify and check application behavior
in a cluster.

There are performed 2 core steps by Amun:

1. Assemble/build the given software by installing requested native packages
   and/or Python packages into a container image. OpenShift's ImageStreams and
   builds are used under the hood.

2. Execute the given application using a script that is provided by a user -
   there are run "inspection jobs" that execute provided user script. All the
   information related to the node where the inspection job was run are
   aggregated.  Such information consists of hardware available (such as CPU,
   CPU flags and features, and such; see `amun-hwinfo
   <https://github.com/thoth-station/amun-hwinfo>`__) as well as information
   from the kernel's process control block (such as number of context switches
   performed, time spent in user/kernel space and such).

The second step is performed if the build succeeded and a user provided a script
to test the application with in the given build environment on the requested
hardware (there are used node selectors in the cluster for this purpose).

The actual second step is used to gather information whether the application
runs with packages being installed in the build step as well as information
such as performance characteristics or any other runtime-related information of
the assembled application.

As Amun accepts purely JSON on its input, the inspection step requires a test
file that is written to disk with an execute flag and run.

All the relevant logs from build and inspection job runs are aggregated and
stored on Ceph together with actual results of inspections.

See `thoth-station/performance
<https://github.com/thoth-station/performance>`__ repository for an example of
a script that can be executed on Amun.

One can see Amun as a CI running in a cluster.

A request to Amun API
=====================

A single request to API is composed of:

* an identifer of the inspection
* a base image itself (e.g. ubi8)
* a list of native packages (RPM or Deb packages) that should be installed into
  the requested base image
* a list of Python packages that should be installed into the requested base
  image in a form of ``Pipfile``/``Pipfile.lock``
* a script (bash, Python or any other scripting language - if the given
  environment knows how to execute the script; if it has required interpreter)
* hardware requirements for pod placement performing builds of application
  stack (installing necessary dependencies)
* hardware requirements for pod placement performing actual application
  execution - "inspection jobs"

See provided OpenAPI/Swagger specification available in this Git repository.
base image is required parameter.

.. figure:: https://raw.githubusercontent.com/thoth-station/amun-api/master/fig/api.gif
   :alt: Amun API exposed supporting OpenAPI.
   :align: center

Monitoring builds and inspections
=================================

Upon a successful request to Amun API, a user obtains an ``inspection_id``.
This identifier is used to reference the given request. On the build endpoints
there are leveraged information about build status and the actual build logs,
on the job endpoints, there are leveraged information about the actual
inspection runs - logs and logs printed to standard output and standard error
stream. These results are obtained on a successful inspection run.

.. figure:: https://raw.githubusercontent.com/thoth-station/amun-api/master/fig/diagram.png
   :alt: Amun service architecture.
   :align: center

Gathering Hardware Configuration
================================

Each time there is created a request with a script run (so there is actually
spawned job responsible for running the provided script), there is run an
init container that gathers information about hardware that is present on
node where the application is run. This information is available in a form of
JSON and becomes part of the actual result of an inspection run.

The Python script that gathers information about hardware present can be
found in
`amun-hwinfo repository <https://github.com/thoth-station/amun-hwinfo>`__.

An example scenario
===================

I, as an Amun user, would like to test performance of optimized TensorFlow
builds available on the
`AICoE Python package index <https://tensorflow.pypi.thoth-station.ninja>`__.
I would like to use:

* TensorFlow provided on AICoE index (provide a  ``Pipfile`` and
  ``Pipfile.lock`` respecting Pipenv configuration to use different package
  indexes)
* Python3, CUDA in specific version, .. - installed as RPMs
* use a cluster node that exposes a GPU with CUDA support
* I would like to use ubi8 as a base image
* I don't need a node with GPU support to assemble/build the TensorFlow
  application
* I provide a Python script that is a TensorFlow application run to gather
  information about TensorFlow (the application can print a JSON with results,
  but can also push data to a remote API stated in the Python script itself).

Amun guarantees the application is built as requested and it is placed on the
correct node inside the cluster given the application requirements (a GPU with
CUDA support).

If the build part fails, the script cannot be run. The build failures can be
observed on exposed build endpoints and are available on Ceph.

REST API client
===============

To comunicate with Amun API, use the autogenerated Swagger client that
available in the
`amun-client repository <https://github.com/thoth-station/amun-client>`__.

Results adapters
================

Library called `thoth-storages <https://github.com/thoth-station/storages>`__
implements `adapters that offer Python interface for accessing inspection files
<https://thoth-station.ninja/docs/developers/storages/thoth.storages.html#module-thoth.storages.inspections>`__.

An example of an inspection
===========================

An example of an Amun inspection request can be found in this repo in examples
directory. The structure corresponds to one inspection placed on Ceph with all
the relevant bits:

.. code-block:: console

   ── inspection-rhtf-conv2d-0f845f38   # inspection id
      ├── build
      │   ├── Dockerfile
      │   ├── log
      │   └── specification
      └── results
          ├── 0
          │   ├── hwinfo
          │   ├── log
          │   └── result
          ├── 1
          │   ├── hwinfo
          │   ├── log
          │   └── result
          └── 2
              ├── hwinfo
              ├── log
              └── result

* ``<inspection-id>/build/Dockerfile`` - automatically
  generated Dockerfile used to build the application, this Dockerfile is a
  transcription of the JSON input to Amun API

* ``<inspection-id>/build/log`` - build log produced during the application
  assembling

* ``<inspection-id>/build/specification`` - whole input (toghether with
  defaults) sent to Amun API endpoints that forms Amun inspection request

All results are indexed, index corresponds to one of the items in the
inspection batch (multiple inspection job runs can be performed with each
request so the application is built just once).

* ``<inspection-id>/results/<num>/hwinfo`` - information about hardware on which the
  inspection job was run (see `thoth-station/amun-hwinfo
  <https://github.com/thoth-station/amun-hwinfo>`__)

* ``<inspection-id>/results/<num>/log`` - inspection run log -- standard error and
  standard output as produced by the inspection script (or any
  library/subprocess it uses).

* ``<inspection-id>/results/<num>/result`` - the actual result of an inspection run
  together with process information from the kernel.

All the results are available on `Ceph
<https://ceph.io/ceph-storage/object-storage/>`__ or any object storage
providing AWS S3 compatible interface.

.. figure:: https://raw.githubusercontent.com/thoth-station/amun-api/master/fig/ceph.gif
   :alt: AWS S3 compatible interface for storing objects.
   :align: center

Argo UI
=======

It's possible to observe how inspections proceed using Argo UI. Argo UI is
exposed on deployment.

.. figure:: https://raw.githubusercontent.com/thoth-station/amun-api/master/fig/argo_ui.gif
   :alt: Argo UI showing inspections.
   :align: center

Deploying the application
=========================

All manifests required to deploy this application are available in
`thoth-station/thoth-application
<https://github.com/thoth-station/thoth-application/tree/master/amun>`__.

License & Copying
=================

This software is released under the terms of GNU General Public License in
version 3.

© Red Hat; AICoE team - Project Thoth
