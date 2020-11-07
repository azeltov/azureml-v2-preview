# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from pathlib import Path
from typing import Iterable, Union, Optional, Any, Dict
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import (
    OnlineEndpointPropertiesTrackedResource, AciComputeConfiguration,
    OnlineEndpointPropertiesTrackedResourceArmPaginatedResult, AksComputeConfiguration,
    BatchEndpointResource, BatchEndpointTrackedResourceArmPaginatedResult, AuthKeys, AuthToken)
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope, OperationsContainer
from azure.ml.constants import (API_VERSION_2020_12_01_PREVIEW, ONLINE_ENDPOINT_TYPE, BATCH_ENDPOINT_TYPE,
                                BASE_PATH_CONTEXT_KEY)
from azure.ml._schema.online_endpoint_schema import OnlineEndpointSchema, InternalOnlineEndpoint
from marshmallow import ValidationError, RAISE
from azure.ml._utils.utils import load_yaml
from .operation_orchestrator import OperationOrchestrator
from azure.ml._schema.code_configuration_schema import InternalCodeConfiguration


class EndpointOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces,
                 all_operations: OperationsContainer):
        super(EndpointOperations, self).__init__(workspace_scope)
        self._client = service_client
        self._online_operation = service_client.online_endpoints
        self._batch_operation = service_client.batch_endpoints
        self._online_deployment = service_client.online_deployments
        self._all_operations = all_operations

    def list(self,
             type: str) -> Union[Iterable[OnlineEndpointPropertiesTrackedResourceArmPaginatedResult],
                                 Iterable[BatchEndpointTrackedResourceArmPaginatedResult]]:
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._online_operation.list(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                api_version=API_VERSION_2020_12_01_PREVIEW)
        elif endpoint_type.lower() == BATCH_ENDPOINT_TYPE:
            return self._batch_operation.list(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                api_version=API_VERSION_2020_12_01_PREVIEW)

    def list_keys(self, type: str, name: str) -> Union[AuthKeys, AuthToken]:
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._get_online_credentials(name=name)
        else:
            return self._get_batch_credentials(name=name)

    def get(self, type: str, name: str) -> Union[OnlineEndpointPropertiesTrackedResource, BatchEndpointResource]:
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._get_online_endpoint(name)
        elif endpoint_type.lower() == BATCH_ENDPOINT_TYPE:
            return self._batch_operation.get(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW)

    def delete(self, type: str, name: str) -> None:
        # TODO: need to delete all the deployments associated with the endpoint
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            self._delete_online_endpoint(name)
        elif endpoint_type.lower() == BATCH_ENDPOINT_TYPE:
            return self._batch_operation.delete(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW)

    def create(self,
               file: Union[str, os.PathLike],
               type: str = None,
               name: Optional[str] = None) -> Union[OnlineEndpointPropertiesTrackedResource, BatchEndpointResource]:
        endpoint_type = self._validate_endpoint_type(type=type)
        if not file:
            raise Exception(f"Please provide yaml file for the creation parameters")

        config = load_yaml(file)
        if not endpoint_type:
            endpoint_type = config["type"]
            self._throw_if_no_endpoint_type(endpoint_type)

        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._create_online_endpoint(config=config, file=file, name=name)
        elif endpoint_type.lower() == BATCH_ENDPOINT_TYPE:
            return self._create_batch_endpoint(config=config)

    def _load_online(self, config: Any, file: Union[str, os.PathLike]) -> InternalOnlineEndpoint:
        context = {BASE_PATH_CONTEXT_KEY: Path(file).parent}
        try:
            schema = OnlineEndpointSchema(context=context)
            return schema.load(config, unknown=RAISE)
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

    def _validate_endpoint_type(self, type: str):
        endpoint_type = type
        if endpoint_type and (endpoint_type.lower() != ONLINE_ENDPOINT_TYPE) and (endpoint_type.lower() != BATCH_ENDPOINT_TYPE):
            raise Exception("Unknown endpoint type {0}".format(endpoint_type))
        return endpoint_type

    def _throw_if_no_endpoint_type(self, endpoint_type: str):
        if not endpoint_type:
            raise Exception("Endpoint type is a required parameter.")

    def _create_online_endpoint(self,
                                config: Any,
                                file: Union[str, os.PathLike],
                                name: Optional[str] = None) -> OnlineEndpointPropertiesTrackedResource:
        internal_endpoint = self._load_online(config, file)
        if not name:
            name = internal_endpoint.name
        if not name:
            raise Exception(f"The endpoint name is required.")

        # TODO: override the yaml settings by the input

        # prepare the assets.
        orchestrators = OperationOrchestrator(self._all_operations)
        for deployment_name, deployment in internal_endpoint.deployments.items():
            if isinstance(deployment.code_configuration, str):
                deployment.code_configuration = InternalCodeConfiguration(
                    code=orchestrators.get_code_asset_arm_id(code_configuration=deployment.code_configuration),
                    scoring_script=None)
            else:
                deployment.code_configuration = InternalCodeConfiguration(
                    code=orchestrators.get_code_asset_arm_id(code_configuration=deployment.code_configuration),
                    scoring_script=deployment.code_configuration.scoring_script)
            deployment.environment = orchestrators.get_environment_arm_id(environment=deployment.environment)
            deployment.model = orchestrators.get_model_arm_id(model=deployment.model)

        # create the endpoint
        endpoint = internal_endpoint._to_rest_online_endpoint()
        self._online_operation.create_or_update(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            body=endpoint,
            api_version=API_VERSION_2020_12_01_PREVIEW)

        # create the deployments
        compute_type = "AMLCompute"
        if isinstance(endpoint.properties.compute_configuration, AksComputeConfiguration):
            compute_type = "AKS"
        elif isinstance(endpoint.properties.compute_configuration, AciComputeConfiguration):
            compute_type = "ACI"
        for deployment_name, deployment in internal_endpoint.deployments.items():
            deployment_rest = deployment._to_rest_online_deployments(compute_type=compute_type,
                                                                     location=internal_endpoint.location)
            self._online_deployment.create_or_update(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                name=deployment_name,
                body=deployment_rest,
                api_version=API_VERSION_2020_12_01_PREVIEW)

        # set the traffic
        endpoint = internal_endpoint._to_rest_online_endpoint_with_traffic()
        return self._online_operation.create_or_update(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            body=endpoint,
            api_version=API_VERSION_2020_12_01_PREVIEW)

    def _get_online_endpoint(self, name: str) -> Dict[str, Any]:
        # first get the endpoint
        endpoint = self._online_operation.get(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW)

        # TODO: Currently the service doesn't support list_by_inference_endpoint, so disable it for now
        # # fetch all the deployments belonging to the endpoint
        # deploymentPagedResult = self._online_deployment.list_by_inference_endpoint(
        #     subscription_id=self._subscription_id,
        #     resource_group_name=self._resource_group_name,
        #     workspace_name=self._workspace_name,
        #     endpoint_name=name,
        #     api_version=API_VERSION_2020_12_01_PREVIEW)
        # endpoint_data = InternalOnlineEndpoint._from_rest(endpoint, deploymentPagedResult)
        # Disable the conversion because there is an issue in the computeConfiguration in swagger
        # endpoint_data = InternalOnlineEndpoint._from_rest(endpoint=endpoint, deployments=None)
        # endpoint_schema = OnlineEndpointSchema()
        # return endpoint_schema.dump(endpoint_data)
        return endpoint

    def _delete_online_endpoint(self, name: str):
        # get all the deployments
        return self._online_operation.delete(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW)

    def _create_batch_endpoint(self, config: Any) -> BatchEndpointResource:
        pass

    def _get_online_credentials(self, name: str) -> Union[AuthKeys, AuthToken]:
        endpoint = self._online_operation.get(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW)
        if endpoint.properties.auth_mode.lower() == "key":
            return self._online_operation.list_keys(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW)
        else:
            return self._online_operation.get_token(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW)

    def _get_batch_credentials(self, name: str) -> Union[AuthKeys, AuthToken]:
        pass