
## Release 0.6.0 (2020-07-01T20:31:44)
* :pushpin: Automatic update of dependency thoth-common from 0.13.13 to 0.14.0
* Allow maintainers to release the application
* Include pre-commit for amun-api
* Add missing Ceph credentials (#444)
* Update OWNERS
* Include thoth-storages to the pipfile
* Relocked pipfile lock
* :pushpin: Automatic update of dependency opentracing-instrumentation from 3.2.1 to 3.3.1
* :sparkles: standard project config files
* Introduce Amun version and service version endpoint
* Do not print results to pod logs
* Introduce batch size and refactor status endpoint
* Obtain results from Ceph instead of OpenShift API
* Add new line after heredoc
* fix aicoe index
* :pushpin: Automatic update of dependency sentry-sdk from 0.14.4 to 0.15.1
* :pushpin: Automatic update of dependency thoth-common from 0.13.8 to 0.13.12
* :pushpin: Automatic update of dependency requests from 2.23.0 to 2.24.0
* :pushpin: Automatic update of dependency more-itertools from 8.3.0 to 8.4.0
* :pushpin: Automatic update of dependency sentry-sdk from 0.14.4 to 0.15.1
* :pushpin: Automatic update of dependency requests from 2.23.0 to 2.24.0
* :pushpin: Automatic update of dependency more-itertools from 8.3.0 to 8.4.0
* :pushpin: Automatic update of dependency prometheus-flask-exporter from 0.13.0 to 0.14.1
* Fix coala warning
* Bump template versions and fix OpenShift version string
* Fix coala complains
* Place results under under inspection name key
* Adjust templates with CPU affinity
* Remove unused results template
* Unify results aggregation
* Use podSpecPatch to propagate resource requests and limits
* Capture hostname in the output
* Adjust inspections to use argo for running inspections
* added a 'tekton trigger tag_release pipeline issue'
* :pushpin: Automatic update of dependency thoth-common from 0.13.7 to 0.13.8
* :pushpin: Automatic update of dependency thoth-common from 0.13.6 to 0.13.7
* :pushpin: Automatic update of dependency prometheus-client from 0.7.1 to 0.8.0
* :pushpin: Automatic update of dependency thoth-common from 0.13.5 to 0.13.6
* :pushpin: Automatic update of dependency thoth-common from 0.13.4 to 0.13.5
* :pushpin: Automatic update of dependency thoth-common from 0.13.3 to 0.13.4
* relocked dependencies due to jsonformatter
* :pushpin: Automatic update of dependency thoth-common from 0.13.1 to 0.13.2
* :pushpin: Automatic update of dependency thoth-common from 0.13.0 to 0.13.1
* :pushpin: Automatic update of dependency connexion from 2.6.0 to 2.7.0
* :pushpin: Automatic update of dependency thoth-common from 0.12.10 to 0.13.0
* :pushpin: Automatic update of dependency thoth-common from 0.12.9 to 0.12.10
* :pushpin: Automatic update of dependency deprecated from 1.2.8 to 1.2.9
* :pushpin: Automatic update of dependency thoth-common from 0.12.7 to 0.12.9
* Make all inspection paths parametrize
* Distinguish cpu and memory for inspection builds and runs
* Update inspection templates
* Be consistent with hwinfo with variable naming
* Add missing parameters to the workflow
* Remove reference to non-existing template
* Create directory structure for results if not exist already
* Add missing parameters to the workflow
* There is no inspection-sync template
* :pushpin: Automatic update of dependency thoth-common from 0.12.6 to 0.12.7
* Remove latest version restriction from .thoth.yaml
* Pin grpcio<1.28
* Increase memory for the build even more
* Fix OOM in the s2i build
* :pushpin: Automatic update of dependency deprecated from 1.2.7 to 1.2.8
* :pushpin: Automatic update of dependency grpcio-tools from 1.27.2 to 1.28.1
* :pushpin: Automatic update of dependency grpcio from 1.27.2 to 1.28.1
* :pushpin: Automatic update of dependency flask from 1.1.1 to 1.1.2
* Revert "Write results to file not to stdandard output"
* Fixed write script
* workflow_id is undefined
* Sync workflow and document IDs
* Do not use generateName use inspection id directly
* Propagate 404 HTTP status code if the inspection was not found
* Fix variable name, inspection_id is undefined
* Add missing imports
* Fix key error if build or run are not present in the specification
* :pushpin: Automatic dependency re-locking
* Write results to file not to stdandard output
* :pushpin: Automatic update of dependency grpcio-tools from 1.27.2 to 1.28.0
* :pushpin: Automatic update of dependency grpcio from 1.27.2 to 1.28.0
* :pushpin: Automatic update of dependency thoth-common from 0.12.5 to 0.12.6
* :pushpin: Automatic update of dependency thoth-common from 0.12.1 to 0.12.5
* Parameters in Workflow template is not read
* :pushpin: Automatic update of dependency thoth-common from 0.10.12 to 0.12.1
* :pushpin: Automatic update of dependency sentry-sdk from 0.14.2 to 0.14.3
* :pushpin: Automatic update of dependency thoth-common from 0.10.11 to 0.10.12
* Remove graph-sync-operator interference from argo workflows
* reverted to older function
* Removed todo to one function
* Added different function for \n
* Move workflow manager logic for amun in Openshift class
* :pushpin: Automatic update of dependency prometheus-flask-exporter from 0.12.2 to 0.13.0
* :pushpin: Automatic update of dependency thoth-common from 0.10.9 to 0.10.11
* Pretty format inspection specification
* Place Dockerfile and specification to inspection artifacts
* Set allowed failures to 0 by default
* Use Thoth's prefix to store output artifacts
* :pushpin: Automatic update of dependency thoth-common from 0.10.8 to 0.10.9
* :pushpin: Automatic update of dependency sentry-sdk from 0.14.1 to 0.14.2
* Fallback if thoth fails to give advise in bc
* No need to create a separate result file, results are part of output
* Increase resources for results gathering task
* Fix path to Python interpreter
* Virtual environment is a directory
* Fix dockerfile formatting
* Add micropipenv support
* Fix schema enum used
* Set imagePullPolicy otherwise pull fails on PSI
* :pushpin: Automatic update of dependency thoth-common from 0.10.7 to 0.10.8
* Removed InspecitonWorkflowParameters from InspectionResponse
* Fix build issues caused by wrong rebase
* Changed OUTPUT_ARTIFACT to THOTH_OUTPUT_ARTIFACT
* Removed duplicated function definition
* Fixed coala issues
* Formatted dockerfile.py
* Changed strings to integers in inspection specification
* Added parsing/unparsing of inspection specification
* Changed `nodes` -> `pods` in job status report
* Improved error handling when parsing pod logs
* Changed InspectionStatus schema
* Minor fixes
* Added missing workflow_status to get_inspection_status
* Added more-itertools to Pipfile to solve version issue
* Fixed Pipfile.lock merge leftover
* Store inspection results according to the schema
* Save output artifacts according to the schema
* Remove excessive `versionchanged` decorators
* Format with Black
* Inspection Workflow API changes
* Retrieve inspection specification from a Workflow
* Updated validate flag according to the upstream
* Increased delay for livenssProbe to 2 hours
* Continue on error as well to collect all outputs
* Removed the deprecated workflow parameter
* Fixed Dockerfile escaping
* Require requirements_locked if requirements are given
* Refactoring the _format_dockerfile function
* Suspend the inspection when exceeded allowed failures
* Modifi artifactRepository in the amun configmap
* Removed artifact suffixes
* Collect inspection build logs as well
* Added configurable affinity parameter
* Re-lock
* Fixed using incorrect inspection build/run templates
* Added template-version annotation to templates
* Fixed missing new line at the end of the file
* Fixed parallelism propagation
* Fixed Dockerfile empty requirements content
* Changed boolean to dict in python additionalProperties
* Fixed typo in post_generate_dockerfile
* Changed Workflow integer parameters to strings
* Added deprecation and versionchanged decorators
* Fixed invalid types in the OpenAPI spec
* Reformat the OpenAPI spec
* Added OpenAPI spec for InspectionWorkflowParameters
* Reduce metadata and annotation length
* Fixed the name of the Workflow with CPU template
* Updated OpenAPI schema for version 0.6.0-dev
* Added inspection workflowtemplates
* Added Amun Role
* [WIP] post_inspection submits the inspection workflow
* Changed steps to DagTasks for easier targetting
* Allow consistent YAML formatting
* Collect inspection results in the last step
* Format dockerfile only in the workflow context
* Added Amun Inspection Workflow template
* Updated Ansible playbooks
* Added processing of Dockerfile for Workflow injection
* :pushpin: Automatic update of dependency thoth-common from 0.10.6 to 0.10.7
* :pushpin: Automatic update of dependency grpcio-tools from 1.27.1 to 1.27.2
* :pushpin: Automatic update of dependency grpcio from 1.27.1 to 1.27.2
* Add inspection_id label
* Adjust ttl to keep objects longer in the cluster
* :pushpin: Automatic update of dependency thoth-common from 0.10.5 to 0.10.6
* Update .thoth.yaml
* :pushpin: Automatic update of dependency prometheus-flask-exporter from 0.12.1 to 0.12.2
* :pushpin: Automatic update of dependency grpcio-tools from 1.26.0 to 1.27.1
* :pushpin: Automatic update of dependency grpcio from 1.26.0 to 1.27.1
* :pushpin: Automatic update of dependency thoth-common from 0.10.4 to 0.10.5
* :pushpin: Automatic update of dependency thoth-common from 0.10.3 to 0.10.4
* :pushpin: Automatic update of dependency thoth-common from 0.10.2 to 0.10.3
* :pushpin: Automatic dependency re-locking
* :pushpin: Automatic update of dependency grpcio-tools from 1.26.0 to 1.27.0
* :pushpin: Automatic update of dependency grpcio from 1.26.0 to 1.27.0
* :pushpin: Automatic update of dependency thoth-common from 0.10.1 to 0.10.2
* :pushpin: Automatic update of dependency thoth-common from 0.10.0 to 0.10.1
* :pushpin: Automatic update of dependency connexion from 2.5.1 to 2.6.0
* Fix escaping of quotes when writing Pipfile.lock
* Force reinstall and upgrade specified Python packages
* :pushpin: Automatic update of dependency thoth-common from 0.9.31 to 0.10.0
* Fix default requests assignment if None was provided on endpoint
* :pushpin: Automatic update of dependency thoth-common from 0.9.30 to 0.9.31
* :pushpin: Automatic update of dependency thoth-common from 0.9.29 to 0.9.30
* :pushpin: Automatic update of dependency sentry-sdk from 0.14.0 to 0.14.1
* :pushpin: Automatic update of dependency thoth-common from 0.9.28 to 0.9.29
* :pushpin: Automatic update of dependency thoth-common from 0.9.27 to 0.9.28
* :pushpin: Automatic update of dependency thoth-common from 0.9.26 to 0.9.27
* :pushpin: Automatic update of dependency jaeger-client from 4.2.0 to 4.3.0
* :pushpin: Automatic update of dependency thoth-common from 0.9.25 to 0.9.26
* :pushpin: Automatic update of dependency thoth-common from 0.9.24 to 0.9.25
* Revert "Remove LC_ALL change locale warning"
* Increase also CPU requirements
* Increase memory requiremetns for example input
* Remove LC_ALL change locale warning
* :pushpin: Automatic update of dependency thoth-common from 0.9.23 to 0.9.24
* Remove line (finally)
* :pushpin: Automatic update of dependency sentry-sdk from 0.13.5 to 0.14.0
* Do not run adviser from bc in debug mode
* :pushpin: Automatic update of dependency thoth-common from 0.9.22 to 0.9.23
* Add field and correct datatype
* Correct datatype inspection output
* Add flag to installer in dockerfile
* Remove node specification
* Add missing label for Amun inspection is
* Happy new year!
* :pushpin: Automatic update of dependency connexion from 2.5.0 to 2.5.1
* :pushpin: Automatic update of dependency grpcio-tools from 1.25.0 to 1.26.0
* :pushpin: Automatic update of dependency grpcio from 1.25.0 to 1.26.0
* :pushpin: Automatic update of dependency connexion from 2.4.0 to 2.5.0
* :pushpin: Automatic update of dependency thoth-common from 0.9.21 to 0.9.22
* Use RHEL instead of UBI
* Update Thoth configuration file and Thoth's s2i configuration
* :pushpin: Automatic update of dependency sentry-sdk from 0.13.4 to 0.13.5
* :pushpin: Automatic update of dependency thoth-common from 0.9.20 to 0.9.21
* :pushpin: Automatic update of dependency thoth-common from 0.9.19 to 0.9.20
* added the missing modules
* added the missing modules
* :pushpin: Automatic update of dependency prometheus-flask-exporter from 0.11.0 to 0.12.0
* :green_heart: relocked, version string something
* :green_heart: we need this level of ignorance
* :pushpin: Automatic update of dependency thoth-common from 0.9.17 to 0.9.19
* :pushpin: Automatic update of dependency thoth-common from 0.9.16 to 0.9.17
* :pushpin: Automatic update of dependency jaeger-client from 4.1.0 to 4.2.0
* :pushpin: Automatic update of dependency gunicorn from 20.0.3 to 20.0.4
* :pushpin: Automatic update of dependency gunicorn from 20.0.2 to 20.0.3
* :pushpin: Automatic update of dependency gunicorn from 20.0.0 to 20.0.2
* Added newlines after dockerfile update string
* :pushpin: Automatic update of dependency thoth-common from 0.9.15 to 0.9.16
* :pushpin: Automatic update of dependency thoth-common from 0.9.14 to 0.9.15
* :pushpin: Automatic update of dependency gunicorn from 19.9.0 to 20.0.0
* Add description
* Add runtime environment
* Added runtime_environment output
* Standardize output for runtime environment
* :pushpin: Automatic update of dependency grpcio-tools from 1.24.3 to 1.25.0
* :pushpin: Automatic update of dependency grpcio from 1.24.3 to 1.25.0
* Add an example inspection job output
* updated templates with annotations and param thoth-advise-value
* Maintain imagestream template for consistency
* :pushpin: Automatic update of dependency grpcio-tools from 1.24.1 to 1.24.3
* :pushpin: Automatic update of dependency grpcio from 1.24.1 to 1.24.3
* :pushpin: Automatic update of dependency connexion from 2.3.0 to 2.4.0
* Add Thoth-Version header
* :pushpin: Automatic update of dependency thoth-common from 0.9.12 to 0.9.14
* :pushpin: Automatic update of dependency thoth-common from 0.9.11 to 0.9.12
* :pushpin: Automatic update of dependency grpcio-tools from 1.24.0 to 1.24.1
* :pushpin: Automatic update of dependency grpcio from 1.24.0 to 1.24.1
* :pushpin: Automatic update of dependency prometheus-flask-exporter from 0.10.0 to 0.11.0
* :pushpin: Automatic update of dependency opentracing-instrumentation from 3.2.0 to 3.2.1
* :pushpin: Automatic update of dependency thoth-common from 0.9.10 to 0.9.11

## Release 0.7.0 (2020-07-07T10:58:55)
* Match results key with adapters

## Release 0.7.1 (2020-07-17T15:32:16)
* :pushpin: Automatic update of dependency thoth-storages from 0.24.3 to 0.24.4 (#469)
* Create & expose service version (#468)
* Let build to accept null (#465)
* :pushpin: Automatic update of dependency thoth-common from 0.14.1 to 0.14.2 (#467)
* :pushpin: Automatic update of dependency sentry-sdk from 0.16.0 to 0.16.1 (#463)
* :pushpin: Automatic update of dependency sentry-sdk from 0.16.0 to 0.16.1 (#462)
* :pushpin: Automatic update of dependency prometheus-flask-exporter from 0.14.1 to 0.15.0 (#461)
* :pushpin: Automatic update of dependency thoth-storages from 0.24.0 to 0.24.3 (#460)
* adding support for amun deployment to thoth-app (#447)
* include aicoe-ci configuration file

## Release 0.7.2 (2020-07-20T16:24:14)
* inspectionstore has attribute build (#472)

## Release 0.7.3 (2020-07-30T15:58:04)
* :pushpin: Automatic update of dependency prometheus-flask-exporter from 0.15.0 to 0.15.4 (#481)
* :pushpin: Automatic update of dependency sentry-sdk from 0.16.1 to 0.16.2
* :pushpin: Automatic update of dependency prometheus-flask-exporter from 0.15.0 to 0.15.4
* :pushpin: Automatic update of dependency thoth-common from 0.14.2 to 0.16.0 (#479)
* :pushpin: Automatic update of dependency thoth-storages from 0.24.4 to 0.25.0 (#480)
* Make started_at nullable (#475)

## Release 0.7.4 (2020-08-07T19:25:13)
* :pushpin: Automatic update of dependency sentry-sdk from 0.16.2 to 0.16.3 (#493)
* Avoid using echo (bashism) (#491)
* Make default requests configurable via env vars (#490)
* Pass -y on apt-get install (#488)

## Release 0.7.5 (2020-08-10T20:59:33)
* Make black happy
* Introduce upgrade pip option
