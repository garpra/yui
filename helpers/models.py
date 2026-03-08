from typing import TypedDict
from dataclasses import dataclass


class ReleaseData(TypedDict):
    success: bool
    app_name: str
    app_path: str
    version: str
    download_url: str
    status: str


class AppPathData(TypedDict):
    desktop_path: str
    icon_path: str


@dataclass
class AppRecord:
    url_type: str
    app_name: str
    app_path: str
    version: str
    download_url: str
    desktop_path: str
    icon_path: str
