from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.repository import StateRepository

FIRMWARE_PATTERN = re.compile(r'^cpe_gateway_v(?P<version>\d+\.\d+\.\d+)\.bin$')


class GatewayService:
    def __init__(self, repository: StateRepository) -> None:
        self.repository = repository

    @staticmethod
    def now_text() -> str:
        return datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')

    @staticmethod
    def short_time() -> str:
        return datetime.now(UTC).strftime('%H:%M')

    def snapshot(self) -> dict[str, Any]:
        return self.repository.load()

    def append_activity(self, state: dict[str, Any], event: str, detail: str) -> None:
        state['activities'].insert(0, {'time': self.short_time(), 'event': event, 'detail': detail})
        state['activities'] = state['activities'][:8]

    def dashboard_context(self) -> dict[str, Any]:
        state = self.snapshot()
        return {
            'system': state['system'],
            'upgrade': state['upgrade'],
            'clients': state['clients'],
            'activities': state['activities'],
        }

    def update_network(self, payload: dict[str, str]) -> dict[str, Any]:
        state = self.snapshot()
        network = state['network']
        network.update(
            {
                'ssid': payload.get('ssid', network['ssid']).strip(),
                'password': payload.get('password', network['password']).strip(),
                'mode': payload.get('mode', network['mode']).strip(),
                'channel': payload.get('channel', network['channel']).strip(),
                'guest_wifi': payload.get('guest_wifi', network['guest_wifi']).strip(),
                'last_saved': self.now_text(),
            }
        )
        self.append_activity(state, '网络参数已更新', f"SSID 已更新为 {network['ssid']}，模式为 {network['mode'].upper()}")
        self.repository.save(state)
        return {'state': state, 'message': '网络配置已保存'}

    def validate_firmware(self, filename: str) -> dict[str, str]:
        filename = filename.strip()
        if not filename:
            return {'status': 'rejected', 'message': '固件文件名不能为空', 'result': '未提供固件文件名，发布已阻断'}

        if not filename.endswith('.bin'):
            return {'status': 'rejected', 'message': '仅允许上传 .bin 固件文件', 'result': '文件后缀不合法，发布已阻断'}

        match = FIRMWARE_PATTERN.match(filename)
        if not match:
            return {
                'status': 'rejected',
                'message': '固件文件名需符合命名规范：cpe_gateway_v主版本.次版本.补丁版本.bin',
                'result': '文件命名不符合发布规范，发布已阻断',
            }

        version = match.group('version')
        return {
            'status': 'validated',
            'message': f'固件 {filename} 校验通过，允许发布',
            'result': f'固件 {filename} 已完成命名规范校验，目标版本为 v{version}',
        }

    def register_firmware(self, filename: str) -> dict[str, Any]:
        state = self.snapshot()
        validation = self.validate_firmware(filename)
        upgrade = state['upgrade']
        upgrade['last_filename'] = filename.strip()
        upgrade['status'] = validation['status']
        upgrade['last_result'] = validation['result']
        upgrade['updated_at'] = self.now_text()

        if validation['status'] == 'validated':
            version = Path(filename).stem.split('_v')[-1]
            state['system']['firmware_version'] = f'v{version}'
            self.append_activity(state, '执行固件校验', validation['result'])
        else:
            self.append_activity(state, '固件校验失败', validation['result'])

        self.repository.save(state)
        return {'state': state, 'message': validation['message'], 'status': validation['status']}

    def run_diagnostics(self) -> dict[str, Any]:
        state = self.snapshot()
        diagnostics = state['diagnostics']
        diagnostics.update(
            {
                'last_run': self.now_text(),
                'gateway_ping': '9 ms',
                'dns_resolution': '正常',
                'cloud_connectivity': '正常',
                'packet_loss': '0%',
            }
        )
        self.append_activity(state, '重新执行运行诊断', '网络连通性、DNS 与云端访问状态均正常')
        self.repository.save(state)
        return {'state': state, 'message': '运行诊断已完成，当前网络环境健康。'}

    def health(self) -> dict[str, Any]:
        state = self.snapshot()
        return {
            'status': 'ok',
            'device_model': state['system']['device_model'],
            'firmware_version': state['system']['firmware_version'],
            'wan_status': state['system']['wan_status'],
            'updated_at': state['upgrade']['updated_at'],
        }
