"""Módulo de definição de constantes globais para o projeto."""

from pathlib import Path
from zoneinfo import ZoneInfo

APP_NAME: str = "py-spotify-playlist"
"""Nome da aplicação: `py-spotify-playlist`"""

VERSION: str = "0.1.0"
"""Versão da aplicação: `0.1.0`"""

LOG_DIR: Path = Path("./logs")
"""Caminho para o diretório de logs: `./logs`"""

SETTINGS_FILE: Path = Path("./src/config/files/settings.yaml")
"""Caminho para o arquivo de configuração global: `./src/config/files/settings.yaml`"""

BRT: ZoneInfo = ZoneInfo("America/Sao_Paulo")
"""Define o objeto de fuso horário para o horário de Brasília:  `America/Sao_Paulo`"""
