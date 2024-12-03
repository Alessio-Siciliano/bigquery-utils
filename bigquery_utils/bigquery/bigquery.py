""" Module to manage all the functions regarding Bigquery. """

from typing import Optional, Union, Dict
from google.cloud.bigquery import Client
from google.cloud.bigquery.job import QueryJobConfig, LoadJobConfig
from google.api_core.client_info import ClientInfo
from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials
import requests


class BigQueryClient(Client):
    """
    BigQuery Client class (child of the original client)
    """

    def __init__(
        self,
        project: Optional[str] = None,
        credentials: Optional[Credentials] = None,
        _http: Optional[requests.Session] = None,
        location: Optional[str] = None,
        default_query_job_config: Optional[QueryJobConfig] = None,
        default_load_job_config: Optional[LoadJobConfig] = None,
        client_info: Optional[ClientInfo] = None,
        client_options: Optional[Union[ClientOptions, Dict]] = None,
    ) -> None:
        super().__init__(
            project,
            credentials,
            _http,
            location,
            default_query_job_config,
            default_load_job_config,
            client_info,
            client_options,
        )

    def get_estimated_bytes_by_query(self, query: str) -> float:
        """Get billing GB for a given query

        Parameters
        ----------
        query:
            Query as string.

        Returns
        -------
        Billed byte
            Total processed byte

        """
        job_config = QueryJobConfig()
        job_config.dry_run = True
        job_config.use_query_cache = False
        query_job = self.query(query=query, job_config=job_config)
        return query_job.total_bytes_processed
