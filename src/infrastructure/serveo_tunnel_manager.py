"""Funções utilitárias para gerenciamento do túnel SSH Serveo."""

import subprocess
import sys
from typing import TYPE_CHECKING

from src.common.base.base_class import BaseClass
from src.config.constants import SETTINGS_FILE
from src.config.settings_manager import SettingsManager
from src.infrastructure.logger import LoggerSingleton
from src.infrastructure.return_handler import ReturnHandler

if TYPE_CHECKING:
    from logging import Logger


class ServeoTunnelManager(BaseClass):
    """Gerencia o túnel SSH Serveo para redirecionamento de portas."""

    def __init__(self, return_handler: ReturnHandler) -> None:
        """Inicializa o gerenciador do túnel com logger e handler."""
        self.logger: Logger = LoggerSingleton.logger or LoggerSingleton.get_logger()
        """Logger singleton para registrar eventos e erros."""

        self.settings = SettingsManager(settings=SETTINGS_FILE)
        """Instância do SettingsManager para acessar configurações do projeto."""

        self.serveo_domain: str = self.settings["serveo"]["domain"]
        """Domínio configurado para o túnel Serveo."""

        self.handler = return_handler
        """Instância do ReturnHandler para gerenciar mensagens de retorno."""

        self.ssh_command = [
            r"C:\Windows\System32\OpenSSH\ssh.exe",
            "-R",
            f"{self.serveo_domain}",
            "serveo.net",
        ]
        """Comando SSH para iniciar o túnel Serveo."""

    def start_tunnel(self) -> subprocess.Popen:
        """Inicia o túnel SSH Serveo em background."""
        try:
            ssh_tunnel_process = subprocess.Popen(
                self.ssh_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.logger.info("Túnel SSH Serveo iniciado com sucesso.")
        except FileNotFoundError:
            self.handler.exception(
                message="Executável SSH não encontrado.",
                exception=FileNotFoundError,
            )
        except OSError:
            self.handler.exception(
                message="Erro ao iniciar túnel SSH Serveo.",
                exception=OSError,
            )
        else:
            return ssh_tunnel_process

    def stop_tunnel(self, proc: subprocess.Popen) -> None:
        """Encerra o processo do túnel SSH Serveo."""
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
                self.logger.info("Túnel SSH Serveo encerrado com sucesso.")
            except subprocess.TimeoutExpired:
                proc.kill()
                self.logger.warning("Forçou encerramento do túnel SSH Serveo após timeout.")
