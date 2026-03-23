from __future__ import annotations

import json
from pathlib import Path

from app.repository import DEFAULT_STATE, StateRepository
from app.services import GatewayService


def build_service(tmp_path: Path) -> tuple[GatewayService, StateRepository]:
    repository = StateRepository(tmp_path / 'state.db')
    repository.save(json.loads(json.dumps(DEFAULT_STATE)))
    return GatewayService(repository, artifact_dir=tmp_path / 'firmware'), repository


def test_update_network_persists_changes(tmp_path):
    service, repository = build_service(tmp_path)

    result = service.update_network(
        {
            'ssid': 'Lab-CPE',
            'password': 'SecurePass123',
            'mode': 'pppoe',
            'channel': '6',
            'guest_wifi': 'disabled',
        }
    )

    state = repository.load()
    assert result['message'] == '网络配置已保存'
    assert state['network']['ssid'] == 'Lab-CPE'
    assert state['network']['mode'] == 'pppoe'
    assert state['network']['guest_wifi'] == 'disabled'
    assert state['activities'][0]['event'] == '网络参数已更新'


def test_register_firmware_accepts_release_filename(tmp_path):
    service, repository = build_service(tmp_path)

    result = service.register_firmware('cpe_gateway_v2.3.1.bin')

    state = repository.load()
    assert result['status'] == 'validated'
    assert '允许发布' in result['message']
    assert state['upgrade']['status'] == 'validated'
    assert state['system']['firmware_version'] == 'v2.3.1'


def test_register_firmware_rejects_invalid_filename(tmp_path):
    service, repository = build_service(tmp_path)

    result = service.register_firmware('firmware-final.bin')

    state = repository.load()
    assert result['status'] == 'rejected'
    assert '命名规范' in result['message']
    assert state['upgrade']['status'] == 'rejected'
    assert state['activities'][0]['event'] == '固件校验失败'


def test_run_diagnostics_updates_state(tmp_path):
    service, repository = build_service(tmp_path)

    result = service.run_diagnostics()

    state = repository.load()
    assert '环境健康' in result['message']
    assert state['diagnostics']['gateway_ping'] == '9 ms'
    assert state['activities'][0]['event'] == '重新执行运行诊断'


def test_export_network_profile_contains_metadata(tmp_path):
    service, _ = build_service(tmp_path)

    result = service.export_network_profile()

    assert 'exported_at' in result
    assert result['network']['ssid'] == 'CPE-5G'
    assert result['system']['device_model'] == 'CPE-X3000'


def test_import_network_profile_validates_required_fields(tmp_path):
    service, repository = build_service(tmp_path)

    result = service.import_network_profile({'ssid': 'OnlyName'})

    state = repository.load()
    assert result['ok'] is False
    assert '缺少必要字段' in result['message']
    assert state['network']['ssid'] == 'CPE-5G'


def test_register_firmware_artifact_records_hashes(tmp_path):
    service, _ = build_service(tmp_path)
    firmware_file = tmp_path / 'cpe_gateway_v2.4.0.bin'
    firmware_file.write_bytes(b'binary-firmware-demo')

    result = service.register_firmware_artifact(
        filename='cpe_gateway_v2.4.0.bin',
        source_type='path',
        source_ref='local-test',
        local_path=str(firmware_file),
        notes='unit test artifact',
    )

    assert result['ok'] is True
    assert result['artifact']['version'] == '2.4.0'
    assert len(result['artifact']['md5']) == 32
    assert len(result['artifact']['sha256']) == 64


def test_execute_upgrade_job_creates_job_and_experiment_run(tmp_path):
    service, repository = build_service(tmp_path)
    firmware_file = tmp_path / 'cpe_gateway_v2.5.0.bin'
    firmware_file.write_bytes(b'binary-firmware-demo-v250')
    artifact = service.register_firmware_artifact(
        filename='cpe_gateway_v2.5.0.bin',
        source_type='git',
        source_ref='commit:abc123',
        local_path=str(firmware_file),
    )['artifact']

    result = service.execute_upgrade_job(int(artifact['id']), trigger_source='git-pipeline')

    state = repository.load()
    assert result['ok'] is True
    assert result['job']['status'] == 'passed'
    assert result['verification']['api_check'] is True
    assert state['system']['firmware_version'] == 'v2.5.0'
    assert service.experiment_summary()['count'] == 1
