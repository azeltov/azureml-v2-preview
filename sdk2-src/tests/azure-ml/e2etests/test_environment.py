import random
import pytest
from azure.core.exceptions import HttpResponseError
from azure.ml import MLClient


@pytest.mark.e2etest
def test_environment_create_or_update_conda(client: MLClient) -> None:
    environment_name = _get_random_string()
    environment_version = 1
    environment = client._environments.create_or_update(
        environment_name=environment_name,
        environment_version=environment_version,
        file="./tests/test_configs/environment/environment_conda.yml",
    )

    environment_id = _get_environment_arm_id(
        client=client, environment_name=environment_name, environment_version=environment_version
    )

    assert environment.properties.conda_file
    assert environment.id == environment_id


def test_environment_create_or_update_conda_no_name(client: MLClient) -> None:
    environment_name = _get_random_string()
    environment_version = 1
    environment = client._environments.create_or_update(
        environment_name=environment_name,
        environment_version=environment_version,
        file="./tests/test_configs/environment/environment_conda_no_name.yml",
    )

    environment_id = _get_environment_arm_id(
        client=client, environment_name=environment_name, environment_version=environment_version
    )

    assert environment
    assert environment.properties.conda_file
    assert environment.id == environment_id


def test_environment_create_or_update_conda_no_name_exception(client: MLClient) -> None:
    with pytest.raises(NameError):
        client._environments.create_or_update(
            environment_name=None,
            environment_version=1,
            file="./tests/test_configs/environment/environment_conda_no_name.yml",
        )


@pytest.mark.e2etest
def test_environment_create_or_update_docker(client: MLClient) -> None:
    environment_name = _get_random_string()
    environment_version = 1
    environment = client._environments.create_or_update(
        environment_name=environment_name,
        environment_version=environment_version,
        file="./tests/test_configs/environment/environment_docker.yml",
    )

    environment_id = _get_environment_arm_id(
        client=client, environment_name=environment_name, environment_version=environment_version
    )

    assert environment
    assert environment.properties.docker.docker_image_uri
    assert environment.id == environment_id


@pytest.mark.e2etest
def test_environment_create_or_update_docker_exception(client: MLClient) -> None:
    environment_name = _get_random_string()
    environment_version = 1
    with pytest.raises(HttpResponseError) as error:
        client._environments.create_or_update(
            environment_name=environment_name,
            environment_version=environment_version,
            file="./tests/test_configs/environment/environment_docker_bad_image.yml",
        )

    assert "Authentication failed for Container Registry" in error.value.message
    assert error.value.status_code == 400


@pytest.mark.e2etest
def test_environment_create_or_update_docker_file(client: MLClient) -> None:
    environment_name = _get_random_string()
    environment_version = 1
    environment = client._environments.create_or_update(
        environment_name=environment_name,
        environment_version=environment_version,
        file="./tests/test_configs/environment/environment_docker_file.yml",
    )

    environment_id = _get_environment_arm_id(
        client=client, environment_name=environment_name, environment_version=environment_version
    )

    assert environment
    assert environment.properties.docker.dockerfile
    assert environment.id == environment_id


@pytest.mark.e2etest
def test_environment_list(client: MLClient) -> None:
    environment_list = client._environments.list()
    assert environment_list


@pytest.mark.e2etest
def test_environment_get(client: MLClient) -> None:
    environment_name = "AzureML-Minimal"
    environment_version = 2
    environment_id = _get_environment_arm_id(
        client=client, environment_name=environment_name, environment_version=environment_version
    )
    environment = client._environments.get(environment_name=environment_name, environment_version=environment_version)

    assert environment
    assert environment.id == environment_id


@pytest.mark.e2etest
def test_environment_get_latest(client: MLClient) -> None:
    environment_name = "AzureML-Minimal"
    environment = client._environments.get_latest_version(environment_name=environment_name)

    assert environment
    environment_id = _get_environment_arm_id(
        client=client, environment_name=environment_name, environment_version=environment.name
    )
    assert environment.id == environment_id


def _get_environment_arm_id(client: MLClient, environment_name: str, environment_version: str) -> str:
    ws_scope = client._workspace_scope
    environment_id = (
        "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{"
        "}/environments/{}/versions/{}".format(
            ws_scope.subscription_id,
            ws_scope.resource_group_name,
            ws_scope.workspace_name,
            environment_name,
            environment_version,
        )
    )

    return environment_id


def _get_random_string():
    return f"test_{str(random.randint(1, 10000000))}"
