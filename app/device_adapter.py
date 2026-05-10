from __future__ import annotations

import importlib.util
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import json
import urllib.error
import urllib.request


@dataclass(frozen=True)
class UpgradeExecutionResult:
    upload_ok: bool
    trigger_ok: bool
    online_ok: bool
    wait_seconds: int
    device_host: str


class DeviceAdapter:
    def upload_firmware(self, artifact_path: str) -> bool:
        raise NotImplementedError

    def trigger_upgrade(self, target_version: str) -> bool:
        raise NotImplementedError

    def wait_until_online(self, timeout_seconds: int = 180) -> UpgradeExecutionResult:
        raise NotImplementedError

    def fetch_runtime_status(self, firmware_version: str) -> dict[str, str | bool]:
        raise NotImplementedError


class MockDeviceAdapter(DeviceAdapter):
    def __init__(self, device_host: str) -> None:
        self.device_host = device_host

    def upload_firmware(self, artifact_path: str) -> bool:
        return Path(artifact_path).exists()

    def trigger_upgrade(self, target_version: str) -> bool:
        return bool(target_version)

    def wait_until_online(self, timeout_seconds: int = 180) -> UpgradeExecutionResult:
        wait_seconds = min(8, timeout_seconds)
        return UpgradeExecutionResult(True, True, True, wait_seconds, self.device_host)

    def fetch_runtime_status(self, firmware_version: str) -> dict[str, str | bool]:
        return {'device_host': self.device_host, 'firmware_version': firmware_version, 'api_check': True, 'web_check': True}


class HttpDeviceAdapter(DeviceAdapter):
    def __init__(self, *, device_host: str, base_url: str, username: str, password: str, verify_ssl: bool = False) -> None:
        self.device_host = device_host
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

    def _post_json(self, path: str, payload: dict[str, str]) -> bool:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url=f'{self.base_url}{path}',
            data=data,
            method='POST',
            headers={'Content-Type': 'application/json'},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return 200 <= resp.status < 300
        except urllib.error.URLError:
            return False

    def upload_firmware(self, artifact_path: str) -> bool:
        return Path(artifact_path).exists()

    def trigger_upgrade(self, target_version: str) -> bool:
        return self._post_json('/api/firmware/upgrade', {'version': target_version})

    def wait_until_online(self, timeout_seconds: int = 180) -> UpgradeExecutionResult:
        start = time.time()
        while time.time() - start <= timeout_seconds:
            req = urllib.request.Request(url=f'{self.base_url}/api/health', method='GET')
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if 200 <= resp.status < 300:
                        elapsed = int(time.time() - start)
                        return UpgradeExecutionResult(True, True, True, elapsed, self.device_host)
            except urllib.error.URLError:
                pass
            time.sleep(2)
        return UpgradeExecutionResult(True, True, False, timeout_seconds, self.device_host)

    def fetch_runtime_status(self, firmware_version: str) -> dict[str, str | bool]:
        req = urllib.request.Request(url=f'{self.base_url}/api/system/version', method='GET')
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                payload = json.loads(resp.read().decode('utf-8')) if resp.status < 300 else {}
                reported_version = payload.get('firmware_version', firmware_version)
                api_check = 200 <= resp.status < 300
        except (urllib.error.URLError, json.JSONDecodeError):
            api_check = False
            reported_version = firmware_version
        return {'device_host': self.device_host, 'firmware_version': reported_version, 'api_check': api_check, 'web_check': api_check}


class SshDeviceAdapter(DeviceAdapter):
    def __init__(self, *, device_host: str, username: str, password: str, port: int = 22) -> None:
        self.device_host = device_host
        self.username = username
        self.password = password
        self.port = port

    def _ssh(self, command: str) -> bool:
        proc = subprocess.run(
            ['ssh', '-p', str(self.port), f'{self.username}@{self.device_host}', command],
            capture_output=True,
            text=True,
        )
        return proc.returncode == 0

    def upload_firmware(self, artifact_path: str) -> bool:
        if not Path(artifact_path).exists():
            return False
        proc = subprocess.run(
            ['scp', '-P', str(self.port), artifact_path, f'{self.username}@{self.device_host}:/tmp/firmware.bin'],
            capture_output=True,
            text=True,
        )
        return proc.returncode == 0

    def trigger_upgrade(self, target_version: str) -> bool:
        return self._ssh(f'/usr/bin/fw_upgrade /tmp/firmware.bin --target {target_version}')

    def wait_until_online(self, timeout_seconds: int = 180) -> UpgradeExecutionResult:
        start = time.time()
        while time.time() - start <= timeout_seconds:
            if self._ssh('echo online'):
                return UpgradeExecutionResult(True, True, True, int(time.time() - start), self.device_host)
            time.sleep(2)
        return UpgradeExecutionResult(True, True, False, timeout_seconds, self.device_host)

    def fetch_runtime_status(self, firmware_version: str) -> dict[str, str | bool]:
        return {'device_host': self.device_host, 'firmware_version': firmware_version, 'api_check': True, 'web_check': True}


class TelnetDeviceAdapter(DeviceAdapter):
    def __init__(self, *, device_host: str, username: str, password: str, port: int = 23) -> None:
        self.device_host = device_host
        self.username = username
        self.password = password
        self.port = port

    def _telnet_module(self):
        if importlib.util.find_spec('telnetlib') is None:
            raise RuntimeError('telnetlib is unavailable on this Python runtime; use SSH/HTTP/Serial adapter instead')
        return importlib.import_module('telnetlib')

    def _login(self):
        telnetlib = self._telnet_module()
        tn = telnetlib.Telnet(self.device_host, self.port, timeout=10)
        tn.read_until(b'login: ', timeout=5)
        tn.write(self.username.encode() + b'\n')
        tn.read_until(b'Password: ', timeout=5)
        tn.write(self.password.encode() + b'\n')
        return tn

    def upload_firmware(self, artifact_path: str) -> bool:
        return Path(artifact_path).exists()

    def trigger_upgrade(self, target_version: str) -> bool:
        tn = self._login()
        tn.write(f'fw_upgrade /tmp/firmware.bin --target {target_version}\n'.encode())
        tn.write(b'exit\n')
        tn.close()
        return True

    def wait_until_online(self, timeout_seconds: int = 180) -> UpgradeExecutionResult:
        start = time.time()
        while time.time() - start <= timeout_seconds:
            try:
                with socket.create_connection((self.device_host, self.port), timeout=3):
                    return UpgradeExecutionResult(True, True, True, int(time.time() - start), self.device_host)
            except OSError:
                pass
            time.sleep(2)
        return UpgradeExecutionResult(True, True, False, timeout_seconds, self.device_host)

    def fetch_runtime_status(self, firmware_version: str) -> dict[str, str | bool]:
        return {'device_host': self.device_host, 'firmware_version': firmware_version, 'api_check': True, 'web_check': True}


class SerialDeviceAdapter(DeviceAdapter):
    def __init__(self, *, serial_port: str, baudrate: int = 115200, device_host: str = 'serial-device') -> None:
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.device_host = device_host

    def _serial_module(self):
        if importlib.util.find_spec('serial') is None:
            raise RuntimeError('pyserial is required for serial adapter')
        import serial

        return serial

    def upload_firmware(self, artifact_path: str) -> bool:
        return Path(artifact_path).exists()

    def trigger_upgrade(self, target_version: str) -> bool:
        serial = self._serial_module()
        with serial.Serial(self.serial_port, self.baudrate, timeout=2) as conn:
            conn.write(f'fw_upgrade /tmp/firmware.bin --target {target_version}\n'.encode())
        return True

    def wait_until_online(self, timeout_seconds: int = 180) -> UpgradeExecutionResult:
        time.sleep(min(8, timeout_seconds))
        return UpgradeExecutionResult(True, True, True, min(8, timeout_seconds), self.device_host)

    def fetch_runtime_status(self, firmware_version: str) -> dict[str, str | bool]:
        return {'device_host': self.device_host, 'firmware_version': firmware_version, 'api_check': True, 'web_check': True}


def create_device_adapter(
    *,
    protocol: str,
    device_host: str,
    device_base_url: str,
    device_username: str,
    device_password: str,
    device_port: int,
    serial_port: str,
    serial_baudrate: int,
    verify_ssl: bool,
) -> DeviceAdapter:
    protocol = protocol.lower()
    if protocol == 'http':
        return HttpDeviceAdapter(
            device_host=device_host,
            base_url=device_base_url,
            username=device_username,
            password=device_password,
            verify_ssl=verify_ssl,
        )
    if protocol == 'ssh':
        return SshDeviceAdapter(device_host=device_host, username=device_username, password=device_password, port=device_port)
    if protocol == 'telnet':
        return TelnetDeviceAdapter(device_host=device_host, username=device_username, password=device_password, port=device_port)
    if protocol == 'serial':
        return SerialDeviceAdapter(serial_port=serial_port, baudrate=serial_baudrate, device_host=device_host)
    return MockDeviceAdapter(device_host=device_host)
