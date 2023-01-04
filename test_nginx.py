import pytest
import requests
from ocp_resources.pod import Pod


@pytest.mark.nginx
def test_nginx_pod(
    webserver_namespace,
    nginx_pod
):
    """
    This test verifies deployed nginx pod is in running state.
    """
    # Extract nginx pod logs
    print(nginx_pod.log())

    # Assert nginx pod is in running state
    nginx_pod_status = nginx_pod.instance.status.phase
    assert nginx_pod_status == Pod.Status.RUNNING


@pytest.mark.nginx
def test_nginx_svc(
    webserver_namespace,
    nginx_pod,
    nginx_svc,
    nginx_route
):
    """
    This test verifies deployed nginx svc is reachable and running.
    """
    # Assert ACK from nginx webserver via exposed nginx-service route
    nginx_res = requests.get(url=f"http://{nginx_route.instance.to_dict()['spec']['host']}")
    assert nginx_res.status_code == 200  # --> OK
