import logging

import io
import os
import pytest
from ocp_resources.pod import Pod
from ocp_resources.route import Route
from ocp_resources.service import Service
from ocp_resources.namespace import Namespace
from ocp_resources.resource import get_client
from ocp_utilities.infra import cluster_resource
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

LOGGER = logging.getLogger(__name__)


def render_yaml_from_dict(template, _dict):
    return io.StringIO(template.render(_dict))


def get_resource_j2_template(template_name, base_templates="templates/"):
    env = Environment(
        loader=FileSystemLoader(base_templates),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    try:
        return env.get_template(name=template_name)
    except TemplateNotFound:
        LOGGER.error(f"Cannot find template {template_name} under {base_templates}")
        raise


@pytest.fixture(scope="session")
def kerberos_user():
    assert os.getenv('KERBEROS_USER'), "Kerberos username is undefined."
    return os.environ['KERBEROS_USER']


@pytest.fixture(scope="session")
def admin_client():
    assert os.getenv('KUBECONFIG'), "Kubeconfig file is missing."
    return get_client(
        config_file=os.environ["KUBECONFIG"]
    )


@pytest.fixture(scope="session")
def webserver_namespace(admin_client, kerberos_user):
    with Namespace(client=admin_client, name=f"webserver-{kerberos_user}") as ws_ns:
        # Wait for ns to be deployed
        ws_ns.wait_for_status(status=Namespace.Status.ACTIVE, timeout=120)
        yield ws_ns


@pytest.fixture(scope="session")
def nginx_pod(admin_client, kerberos_user):
    # Initializing pod manifest yaml based on current user
    pod_manifest_template = get_resource_j2_template("nginx_pod_manifest.j2")
    pod_manifest_yaml = render_yaml_from_dict(
        template=pod_manifest_template,
        _dict={
            'kerberos_user': kerberos_user
        }
    )

    with cluster_resource(Pod)(client=admin_client, yaml_file=pod_manifest_yaml) as nginx_pod:
        # Wait for pod to be deployed
        nginx_pod.wait_for_status(status=Pod.Status.RUNNING, timeout=120)
        yield nginx_pod


@pytest.fixture(scope="session")
def nginx_svc(admin_client, kerberos_user):
    # Initializing svc manifest yaml based on current user
    svc_manifest_template = get_resource_j2_template("nginx_svc_manifest.j2")
    svc_manifest_yaml = render_yaml_from_dict(
        template=svc_manifest_template,
        _dict={
            'kerberos_user': kerberos_user
        }
    )

    with cluster_resource(Service)(client=admin_client, yaml_file=svc_manifest_yaml) as nginx_svc:
        yield nginx_svc


@pytest.fixture(scope="session")
def nginx_route(admin_client, kerberos_user, nginx_svc):
    # Exposing nginx service route
    with cluster_resource(Route)(client=admin_client, name='nginx-route', namespace=f'webserver-{kerberos_user}',
                                 service=nginx_svc.instance.to_dict()['metadata']['name']) as nginx_route:
        yield nginx_route
