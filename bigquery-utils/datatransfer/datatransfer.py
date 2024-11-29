""" Module to extend the original DataTransferServiceClient. """

import re
from typing import Optional, Sequence, Tuple, Union
from google.cloud.bigquery_datatransfer import DataTransferServiceClient
from google.auth.credentials import Credentials
from google.cloud.bigquery_datatransfer_v1.services.data_transfer_service.pagers import (  # pylint: disable=line-too-long
    ListTransferConfigsPager,
)
from google.cloud.bigquery_datatransfer_v1.types.datatransfer import (
    ListTransferConfigsRequest,
)
from google.api_core.retry import Retry
from google.api_core.gapic_v1.method import _MethodDefault
from google.cloud.bigquery_datatransfer_v1.types.transfer import TransferConfig


class DataTransferClient(DataTransferServiceClient):
    """
    Custom class of DataTransferServiceClient
    """

    # Matching rule for the format of a Scheduled Query ID.
    MATCHING_RULE_TRANSFER_CONFIG_ID = (
        ""
        r"projects\/[a-zA-Z0-9-]+\/locations\/[a-zA-Z-]+\/transferConfigs\/[a-zA-Z0-9-]+"  # pylint: disable=line-too-long
    )

    # Matching rule for the format of a parent string.
    MATCHING_RULE_PROJECT_LOCATION = (
        r"projects\/[a-zA-Z0-9-]+\/locations\/[a-zA-Z-]+"
    )

    def __init__(
        self,
        credentials: Optional[Credentials] = None,
        client_options: Optional[dict] = None,
    ) -> None:
        """
        Init of the class, same as parent

        Parameters
        ----------
        credentials : Optional[Credentials]
            credentials of the current user

        client_options: Optional[dict]
            custom client settings

        Returns
        -------
        None
        """
        super().__init__(
            credentials=credentials, client_options=client_options
        )
        self.cached_iterator: dict = {}
        # ListTransferConfigsPager | None = None

    def list_transfer_configs(
        self,
        request: Optional[Union[ListTransferConfigsRequest, dict]] = None,
        *,
        parent: Optional[str] = None,
        retry: Optional[Union[Retry, _MethodDefault, None]] = None,
        timeout: Optional[Union[float, object]] = None,
        metadata: Sequence[Tuple[str, str]] = (),
        with_email: bool = False,
    ) -> ListTransferConfigsPager:
        """Get ALL schedule queries of the project.

        Parameters
        ----------
        request:
            A request to list data transfers configured for a BigQuery project.

        parent:
            The BigQuery project id, it should be returned:
                projects/{project_id}/locations/{location_id}

        retry:
            Designation of what errors, if any, should be retried.

        timeout: float
            The timeout for this request.

        metadata: Sequence[Tuple[str, str]]
            Sequence of metadata as the original function.

        with_email: bool
            this field makes another request to get the owner_email.
            Default value is False to avoid useless requests.

        Returns
        -------
        ListTransferConfigsPager
            Iterator of the TransConfigPager

        """

        # If request is a dict(), convert to ListTransferConfigsRequest
        if isinstance(request, dict):
            request = ListTransferConfigsRequest(**request)

        # At least one between request and parent should be not empty
        if (request is None or not request.parent) and not parent:
            raise ValueError("Request or parent parameters must be provided!")

        if (
            parent is not None
            and re.match(self.MATCHING_RULE_PROJECT_LOCATION, parent) is None
        ):
            raise ValueError(
                "Parent should be in the format projects/{}/locations/{}"
            )

        transfer_configs_request_response = super().list_transfer_configs(
            request=request,
            parent=parent,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )
        if with_email:
            # For each TransferConfig we make a single request to get the email
            for transfer_config in transfer_configs_request_response:
                # If the data format is correct, let's try with the request
                transfer_config_email = self.get_transfer_config(
                    name=transfer_config.name
                ).owner_info
                setattr(transfer_config, "owner_info", transfer_config_email)

        self.cached_iterator[with_email] = transfer_configs_request_response
        return transfer_configs_request_response

    def list_transfer_config_by_owner_email(
        self, owner_email: str, project_id: str
    ) -> list[TransferConfig]:
        """Get ALL schedule queries of a given user.

        Parameters
        ----------
        owner_email:
            Owner of the scheduled query.

        parent:
            The BigQuery project id, it should be returned:
                projects/{project_id}/locations/{location_id}

        Returns
        -------
        list[TransferConfig]
            List of all TransferConfig object

        """

        # If not cached, run it
        if True not in self.cached_iterator:
            self.cached_iterator[True] = self.list_transfer_configs(
                parent=project_id, with_email=True
            )

        return list(
            filter(
                lambda x: x.owner_info.email == owner_email,
                self.cached_iterator[True],
            )
        )
