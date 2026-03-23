from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UpgradeExecutionResult:
    upload_ok: bool
    trigger_ok: bool
    online_ok: bool
    wait_seconds: int
    device_host: str


class MockDeviceAdapter:
    def __init__(self, device_host: str) -> None:
        self.device_host = device_host

    def upload_firmware(self, artifact_path: str) -> bool:
        return Path(artifact_path).exists()

    def trigger_upgrade(self, target_version: str) -> bool:
        return bool(target_version)

    def wait_until_online(self, timeout_seconds: int = 180) -> UpgradeExecutionResult:
        wait_seconds = min(8, timeout_seconds)
        return UpgradeExecutionResult(
            upload_ok=True,
            trigger_ok=True,
            online_ok=True,
            wait_seconds=wait_seconds,
            device_host=self.device_host,
        )

    def fetch_runtime_status(self, firmware_version: str) -> dict[str, str | bool]:
        return {
            'device_host': self.device_host,
            'firmware_version': firmware_version,
            'api_check': True,
            'web_check': True,
        }
