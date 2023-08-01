import dataclasses
from itertools import cycle

from typing import Literal

from textual.app import App, ComposeResult
from textual.widgets import Header, OptionList, DataTable

from tuinator.repositories import RedmineApiClient


@dataclasses.dataclass
class SortingColumn:
    column_key: str
    reversed: bool = False

    def reverse(self):
        self.reversed = not self.reversed

    def __eq__(self, other):
        if isinstance(other, str):
            return self.column_key == other

    def __ne__(self, other):
        if isinstance(other, str):
            return self.column_key != other


class IssuesList(OptionList):
    def on_mount(self):
        redmine_issues = RedmineApiClient(
            "https://redmine.deployed.pl", "78b3bdd3518dd6eea9495254e14db067780f9375"
        ).get_issues_by_user(129)
        for issue in redmine_issues:
            self.add_option(
                f"{issue.internal_id} - {issue.subject} - {issue.assigned_to}"
            )


class IssueTable(DataTable):
    cursors = cycle(["column", "row"])

    def __init__(
        self,
        *,
        show_header: bool = True,
        show_row_labels: bool = True,
        fixed_rows: int = 0,
        fixed_columns: int = 0,
        zebra_stripes: bool = False,
        header_height: int = 1,
        show_cursor: bool = True,
        cursor_foreground_priority: Literal["renderable", "css"] = "css",
        cursor_background_priority: Literal["renderable", "css"] = "renderable",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            show_header=show_header,
            show_row_labels=show_row_labels,
            fixed_rows=fixed_rows,
            fixed_columns=fixed_columns,
            zebra_stripes=zebra_stripes,
            header_height=header_height,
            show_cursor=show_cursor,
            cursor_foreground_priority=cursor_foreground_priority,
            cursor_background_priority=cursor_background_priority,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._cursors = cycle(("row", "column"))
        self.cursor_type = next(self.cursors)
        self._columns = ("ID", "Status", "Subject", "Author", "Assignee")
        self._current_sort: SortingColumn | None = None
        self._user_id = 127

    def on_mount(self):
        redmine_issues = RedmineApiClient(
            "https://redmine.deployed.pl", "78b3bdd3518dd6eea9495254e14db067780f9375"
        ).get_issues_by_user(self._user_id)
        self.clear(columns=True)
        for column in self._columns:
            self.add_column(column, key=column.lower())
        for issue in redmine_issues:
            self.add_row(
                issue.id,
                issue.status.name,
                issue.subject,
                issue.author.name,
                issue.assigned_to.name,
            )

    def key_c(self):
        self.cursor_type = next(self.cursors)

    def key_f6(self):
        if self.cursor_type == "column":
            sorting_column = self._columns[self.cursor_column].lower()
            if (not self._current_sort) or self._current_sort != sorting_column:
                self._current_sort = SortingColumn(sorting_column)
            else:
                self._current_sort.reverse()
            self.sort(
                self._current_sort.column_key, reverse=self._current_sort.reversed
            )

    def key_r(self):
        self._user_id += 1
        self.on_mount()


class TuinatorApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Header(True, name="Tuinator")
        yield IssueTable()
