import abc
from collections.abc import Iterable
from functools import cached_property

from redminelib import Redmine
from redminelib.resources import Issue, User


class BaseIssueRepository(abc.ABC):
    @abc.abstractmethod
    def get_issues_by_user(self, user_id: int):
        pass


class RedmineApiClient:
    def __init__(self, endpoint: str, api_key: str):
        self._endpoint = endpoint
        self._api_key = api_key
        self._client = Redmine(
            endpoint, key=api_key, requests={"auth": ("admin", "haslo")}
        )

    @cached_property
    def current_user(self) -> User:
        return self._client.user.get("current")

    def get_issues_by_user(self, user_id: int) -> Iterable[Issue]:
        return self._client.issue.filter(assigned_to_id=user_id, limit=100)


class ApiIssueRepository(BaseIssueRepository):
    def __init__(self, api_client: RedmineApiClient):
        self.api_client = api_client

    def get_issues_by_user(self, user_id: int):
        return self.api_client.get_issues_by_user(user_id)
