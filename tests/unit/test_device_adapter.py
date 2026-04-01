from __future__ import annotations

from app.device_adapter import MockDeviceAdapter, create_device_adapter


def test_create_device_adapter_returns_mock_when_protocol_unknown():
    adapter = create_device_adapter(
        protocol='unknown',
        device_host='192.168.1.1',
        device_base_url='http://192.168.1.1',
        device_username='admin',
        device_password='admin',
        device_port=22,
        serial_port='/dev/ttyUSB0',
        serial_baudrate=115200,
        verify_ssl=False,
    )

    assert isinstance(adapter, MockDeviceAdapter)


def test_mock_adapter_basic_flow(tmp_path):
    fw = tmp_path / 'fw.bin'
    fw.write_bytes(b'abc')
    adapter = MockDeviceAdapter('127.0.0.1')

    assert adapter.upload_firmware(str(fw)) is True
    assert adapter.trigger_upgrade('2.0.0') is True
    result = adapter.wait_until_online(timeout_seconds=5)
    assert result.online_ok is True
