#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pydantic==2.12.5",
# ]
# ///

from pydantic import BaseModel, ConfigDict

import json
import os
import subprocess
import time
from enum import StrEnum
from typing import Callable, Iterator, List, Tuple


BAR_HEIGHT = int(os.getenv("WAYBAR_AUTOHIDE_BAR_HEIGHT", "50"))
HEIGHT_THRESHOLD = int(os.getenv("WAYBAR_AUTOHIDE_HEIGHT_THRESHOLD", "20"))
WAYBAR_PROC = os.getenv("WAYBAR_AUTOHIDE_PROCNAME", "waybar")


class WaybarState(StrEnum):
    VISIBLE = "1"
    HIDDEN = "0"


class Workspace(BaseModel):
    id: int
    name: str


class HyprlandClient(BaseModel):
    model_config = ConfigDict(extra="ignore")

    address: str
    mapped: bool
    hidden: bool

    at: Tuple[int, int]
    size: Tuple[int, int]

    workspace: Workspace
    monitor: int
    fullscreen: int


def toggle_waybar_visibility():
    subprocess.run(["pkill", "-USR1", WAYBAR_PROC], check=False)


def get_current_workspace() -> list[int]:
    workspaces = subprocess.check_output(
        "hyprctl monitors -j | jq '.[] | .activeWorkspace.id'",
        shell=True,
        text=True,
    )
    return [int(workspace.strip()) for workspace in workspaces.strip().split("\n")]


def get_monitor_from_position(pos_x: int, pos_y: int) -> int | None:
    monitors = json.loads(subprocess.check_output(["hyprctl", "-j", "monitors"]))

    for monitor in monitors:
        start_x, end_x = monitor["x"], monitor["x"] + monitor["width"]
        start_y, end_y = monitor["y"], monitor["y"] + monitor["height"]

        if pos_x < start_x or pos_x > end_x:
            continue

        if pos_y < start_y or pos_y > end_y:
            continue

        return int(monitor["id"])

    return None


def get_clients(
    filter_func: Callable[[HyprlandClient], bool] | None = None,
) -> Iterator[HyprlandClient]:
    clients = [
        HyprlandClient.model_validate(c)
        for c in json.loads(subprocess.check_output(["hyprctl", "-j", "clients"]))
    ]
    for c in clients:
        if filter_func is None or filter_func(c):
            yield c


def get_overlapping_clients(
    active_workspaces: list[int],
    monitors: list[int] | None = None,
) -> Iterator[HyprlandClient]:
    def overlaps_bar(c: HyprlandClient) -> bool:
        if not c.mapped:
            return False
        if c.hidden:
            return False
        if c.fullscreen:
            return False
        if c.monitor not in (monitors or [c.monitor]):
            return False
        if c.workspace.id not in active_workspaces:
            return False

        x, y = c.at
        w, h = c.size

        return y < (BAR_HEIGHT + HEIGHT_THRESHOLD) and (y + h) > 0

    return get_clients(overlaps_bar)


def window_overlaps_bar(
    active_workspaces: list[int], monitors: List[int] | None = None
) -> bool:
    return any(get_overlapping_clients(active_workspaces, monitors))


def get_cursor_position() -> Tuple[int, int]:
    output = subprocess.check_output(["hyprctl", "cursorpos"]).decode()
    pos_x, pos_y = output.strip().split(",")
    return int(pos_x.strip()), int(pos_y.strip())


def cursor_aproaches_bar(monitors: list[int] | None, current_state: WaybarState) -> bool:
    x, y = get_cursor_position()

    cursor_monitor = get_monitor_from_position(x, y)
    if cursor_monitor is None or cursor_monitor not in (monitors or [cursor_monitor]):
        return False

    offset = BAR_HEIGHT if current_state == WaybarState.VISIBLE else 0

    return y <= offset


def handle():
    waybar_monitors = os.environ.get("WAYBAR_AUTOHIDE_MONITORS", None)
    if waybar_monitors is not None:
        waybar_monitors = waybar_monitors.split(",")
        waybar_monitors = [int(m.strip()) for m in waybar_monitors if m.strip()]

    state: WaybarState = WaybarState(
        os.environ.get("WAYBAR_AUTOHIDE_STATE", "1")
    )

    refresh_rate = float(os.environ.get("WAYBAR_AUTOHIDE_REFRESH_RATE", "0.5"))

    while True:
        time.sleep(refresh_rate)

        cursor_aproaches = cursor_aproaches_bar(waybar_monitors, state)

        if cursor_aproaches and state == WaybarState.VISIBLE:
            continue

        if cursor_aproaches and state == WaybarState.HIDDEN:
            toggle_waybar_visibility()
            state = WaybarState.VISIBLE
            continue

        active_workspaces = get_current_workspace()

        overlaps = window_overlaps_bar(active_workspaces, waybar_monitors)

        if overlaps and state == WaybarState.VISIBLE:
            toggle_waybar_visibility()
            state = WaybarState.HIDDEN
            continue

        if not overlaps and state == WaybarState.HIDDEN:
            toggle_waybar_visibility()
            state = WaybarState.VISIBLE


if __name__ == "__main__":
    handle()
