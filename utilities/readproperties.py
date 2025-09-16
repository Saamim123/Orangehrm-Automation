from __future__ import annotations
import os
from pathlib import Path
import configparser
from typing import Optional, Any

class ReadConfig:
    """
    Robust config helper:
    - loads config once from project/configuration/config.ini by default
    - supports environment variable overrides (recommended for secrets)
    - provides typed getters with optional fallbacks
    """

    _config: configparser.ConfigParser | None = None
    _config_path: Path | None = None

    @classmethod
    def _ensure_loaded(cls, path: Optional[Path] = None) -> None:
        if cls._config is not None:
            return

        # default path: <project root>/configuration/config.ini
        cls._config_path = (path or Path.cwd() / "configuration" / "config.ini").resolve()

        if not cls._config_path.exists():
            raise FileNotFoundError(f"Config file not found: {cls._config_path}")

        parser = configparser.ConfigParser()
        # optional: enable interpolation: configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        parser.read(cls._config_path, encoding="utf-8")
        cls._config = parser

    @classmethod
    def reload(cls, path: Optional[Path] = None) -> None:
        """Force re-read (useful for tests that modify the file)."""
        cls._config = None
        cls._ensure_loaded(path)

    @classmethod
    def _get_raw(cls, section: str, key: str, fallback: Optional[str] = None) -> Optional[str]:
        cls._ensure_loaded()
        assert cls._config is not None
        try:
            return cls._config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    @classmethod
    def get(cls, section: str, key: str, fallback: Optional[str] = None, env_var: Optional[str] = None) -> Optional[str]:
        """
        Generic get that allows overriding via environment variable.
        Example: ReadConfig.get('common info','admin_email', env_var='ADMIN_EMAIL')
        """
        # environment variable override (preferred for secrets/CI)
        if env_var:
            val = os.getenv(env_var)
            if val is not None:
                return val

        return cls._get_raw(section, key, fallback=fallback)

    @classmethod
    def get_int(cls, section: str, key: str, fallback: Optional[int] = None, env_var: Optional[str] = None) -> Optional[int]:
        raw = cls.get(section, key, None, env_var=env_var)
        if raw is None:
            return fallback
        try:
            return int(raw)
        except ValueError:
            raise ValueError(f"Config value for [{section}]{key} is not an int: {raw!r}")

    @classmethod
    def get_bool(cls, section: str, key: str, fallback: Optional[bool] = None, env_var: Optional[str] = None) -> Optional[bool]:
        raw = cls.get(section, key, None, env_var=env_var)
        if raw is None:
            return fallback
        return cls._config.getboolean(section, key)

    # ---- convenience wrappers for your keys ----
    @classmethod
    def get_user_login_url(cls) -> str:
        return cls.get("common info", "user_login_url", env_var="ADMIN_LOGIN_URL") or ""

    @classmethod
    def get_user_email(cls) -> str:
        return cls.get("common info", "user_email", env_var="ADMIN_EMAIL") or ""

    @classmethod
    def get_user_password(cls) -> str:
        # Prefer environment variable for secrets in CI
        return cls.get("common info", "user_password", env_var="ADMIN_PASSWORD") or ""



    @classmethod
    def get_search_item_name(cls) -> str:
        return cls.get("common info", "search_item") or ""

    @classmethod
    def get_emp_initial_name(cls) -> str:
        # Prefer environment variable for secrets in CI
        return cls.get("common info", "pim_emp_name", env_var="ADMIN_PASSWORD") or ""

