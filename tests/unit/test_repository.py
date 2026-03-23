from __future__ import annotations

from app.repository import DEFAULT_STATE, StateRepository


def test_repository_initializes_default_state(tmp_path):
    repository = StateRepository(tmp_path / 'state.json')

    state = repository.load()

    assert state['system']['device_model'] == DEFAULT_STATE['system']['device_model']
    assert state['network']['ssid'] == DEFAULT_STATE['network']['ssid']


def test_repository_reset_restores_defaults(tmp_path):
    repository = StateRepository(tmp_path / 'state.json')
    state = repository.load()
    state['network']['ssid'] = 'Changed'
    repository.save(state)

    reset_state = repository.reset()

    assert reset_state['network']['ssid'] == DEFAULT_STATE['network']['ssid']
