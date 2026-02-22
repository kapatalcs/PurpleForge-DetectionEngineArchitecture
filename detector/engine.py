from collections import defaultdict, deque
from datetime import timedelta
from typing import List
import yaml
import sqlite3

from detector.event import Event
from detector.rules.baserule import BaseRule
from core.config_loader import ConfigLoader


class PurpleForgeDetectionEngine:

    def __init__(self, rules: List[BaseRule], window_seconds: int = 300):
        self.rules = rules
        self.window = timedelta(seconds=window_seconds)

        self.events_by_ip = defaultdict(deque)
        self.events_by_user = defaultdict(deque)

        config_loader = ConfigLoader()
        self.labs_config = config_loader.get_lab_config()

        self.known_users_by_lab = defaultdict(set)
        self._load_lab_users()

        with open("mapping/mapping.yaml") as f:
            self.mitre_mapping = yaml.safe_load(f)


    def process(self, event: Event):
        self._expire_for_ip(event.ip, event.timestamp)
        if event.user:
            self._expire_for_user(event.user, event.timestamp)

        self._store_event(event)

        alerts = []
        for rule in self.rules:
            alert = rule.match(event, self)
            if alert:
                mapping = self.mitre_mapping.get(rule.name, {})
                alert["rule"] = rule.name
                alert["mitre"] = mapping
                alerts.append(alert)

        return alerts

    def _store_event(self, event: Event):
        self.events_by_ip[event.ip].append(event)
        if event.user:
            self.events_by_user[event.user].append(event)


    def _expire_for_ip(self, ip: str, now):
        queue = self.events_by_ip.get(ip)
        if not queue:
            return

        cutoff = now - self.window

        if queue[0].timestamp.tzinfo and cutoff.tzinfo is None:
            cutoff = cutoff.replace(tzinfo=queue[0].timestamp.tzinfo)

        while queue and queue[0].timestamp < cutoff:
            queue.popleft()

        if not queue:
            del self.events_by_ip[ip]

    def _expire_for_user(self, user: str, now):
        queue = self.events_by_user.get(user)
        if not queue:
            return

        cutoff = now - self.window

        if queue[0].timestamp.tzinfo and cutoff.tzinfo is None:
            cutoff = cutoff.replace(tzinfo=queue[0].timestamp.tzinfo)

        while queue and queue[0].timestamp < cutoff:
            queue.popleft()

        if not queue:
            del self.events_by_user[user]


    def get_events_by_ip(self, ip: str):
        return list(self.events_by_ip.get(ip, []))

    def get_events_by_user(self, user: str):
        return list(self.events_by_user.get(user, []))


    def _load_lab_users(self):
        for lab, cfg in self.labs_config.items():
            db_path = cfg.get("database_path")
            if not db_path:
                continue
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users")
                rows = cursor.fetchall()
                self.known_users_by_lab[lab] = {r[0] for r in rows}
                conn.close()
            except Exception:
                self.known_users_by_lab[lab] = set()

    def user_exists(self, lab: str, user: str) -> bool:
        if not lab:
            return False
        users = self.known_users_by_lab.get(lab)
        if users is None:
            return False
        return user in users