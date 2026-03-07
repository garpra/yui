from typing import TypedDict
from dataclasses import dataclass


class ReleaseData(TypedDict):
    success: bool
    app_name: str | None
    app_path: str | None
    version: str | None
    download_url: str | None
    status: str


class AppPathData(TypedDict):
    desktop_path: str
    icon_path: str


@dataclass
class AppRecord:
    app_name: str
    app_path: str
    version: str
    download_url: str
    desktop_path: str
    icon_path: str
