from __future__ import annotations

import json
import sqlite3
from copy import deepcopy
from pathlib import Path
from typing import Any


DEFAULT_STATE: dict[str, Any] = {
    'network': {
        'ssid': 'CPE-5G',
        'password': 'ChangeMe123',
        'mode': 'dhcp',
        'channel': 'Auto',
        'guest_wifi': 'enabled',
        'last_saved': '2026-03-20 10:00 UTC',
    },
    'upgrade': {
        'last_filename': 'cpe_gateway_v2.0.3.bin',
        'status': 'validated',
        'last_result': '上一版固件已通过发布前校验',
        'updated_at': '2026-03-21 08:30 UTC',
    },
    'system': {
        'device_model': 'CPE-X3000',
        'firmware_version': 'v2.0.3',
        'uptime': '14 days',
        'wan_status': 'Online',
        'lan_clients': 18,
        'cpu_usage': '24%',
        'memory_usage': '58%',
    },
    'clients': [
        {'name': 'Office-Laptop', 'ip': '192.168.1.12', 'band': '5GHz', 'quality': 'Excellent'},
        {'name': 'Meeting-Room-TV', 'ip': '192.168.1.28', 'band': '2.4GHz', 'quality': 'Good'},
        {'name': 'QA-Phone', 'ip': '192.168.1.41', 'band': '5GHz', 'quality': 'Excellent'},
    ],
    'activities': [
        {'time': '09:12', 'event': '自动化冒烟测试通过', 'detail': '登录、网络配置、升级页校验全部成功'},
        {'time': '08:40', 'event': '部署新测试环境', 'detail': 'Docker 测试容器重新初始化完成'},
        {'time': '07:55', 'event': '发现新固件包', 'detail': '等待执行升级前门禁校验'},
    ],
    'diagnostics': {
        'last_run': '2026-03-21 09:15 UTC',
        'gateway_ping': '12 ms',
        'dns_resolution': '正常',
        'cloud_connectivity': '正常',
        'packet_loss': '0%',
    },
}


class StateRepository:
    def __init__(self, database_path: str | Path, seed_path: str | Path | None = None) -> None:
        self.database_path = Path(database_path)
        self.seed_path = Path(seed_path) if seed_path else None
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
        if not self._has_data():
            self.reset()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                '''
                CREATE TABLE IF NOT EXISTS singleton_state (
                    section TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    band TEXT NOT NULL,
                    quality TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT NOT NULL,
                    event TEXT NOT NULL,
                    detail TEXT NOT NULL
                );
                '''
            )

    def _has_data(self) -> bool:
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM singleton_state").fetchone()
            return bool(row['count'])

    def _seed_state(self) -> dict[str, Any]:
        if self.seed_path and self.seed_path.exists():
            with self.seed_path.open('r', encoding='utf-8') as file:
                return json.load(file)
        return deepcopy(DEFAULT_STATE)

    def load(self) -> dict[str, Any]:
        with self._connect() as connection:
            singleton_rows = connection.execute("SELECT section, payload FROM singleton_state").fetchall()
            state = {row['section']: json.loads(row['payload']) for row in singleton_rows}
            state['clients'] = [dict(row) for row in connection.execute("SELECT name, ip, band, quality FROM clients ORDER BY id").fetchall()]
            state['activities'] = [dict(row) for row in connection.execute("SELECT time, event, detail FROM activities ORDER BY id ASC").fetchall()]
            return state

    def save(self, state: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as connection:
            for section in ('network', 'upgrade', 'system', 'diagnostics'):
                connection.execute(
                    '''
                    INSERT INTO singleton_state(section, payload)
                    VALUES(?, ?)
                    ON CONFLICT(section) DO UPDATE SET payload=excluded.payload
                    ''',
                    (section, json.dumps(state[section], ensure_ascii=False)),
                )

            connection.execute('DELETE FROM clients')
            connection.executemany(
                'INSERT INTO clients(name, ip, band, quality) VALUES(?, ?, ?, ?)',
                [(client['name'], client['ip'], client['band'], client['quality']) for client in state['clients']],
            )

            connection.execute('DELETE FROM activities')
            connection.executemany(
                'INSERT INTO activities(time, event, detail) VALUES(?, ?, ?)',
                [(item['time'], item['event'], item['detail']) for item in state['activities']],
            )
        return state

    def reset(self) -> dict[str, Any]:
        state = self._seed_state()
        return self.save(state)
