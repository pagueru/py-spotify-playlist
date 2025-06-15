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
        self.logger.info("Inicializando com ReturnHandler.")
        self.settings = SettingsManager()
        self.serveo_domain: str = self.settings.settings["serveo"]["domain"]
        self.logger.info(f"Domínio Serveo configurado: {self.serveo_domain}")
        self.handler = return_handler
        self.ssh_command = [
            r"C:\Windows\System32\OpenSSH\ssh.exe",
            "-R",
            f"{self.serveo_domain}",
            "serveo.net",
        ]
        self.logger.info(f"Comando SSH configurado: {self.ssh_command}")

    def start_tunnel(self) -> subprocess.Popen:
        """Inicia o túnel SSH Serveo em background."""
        self.logger.info("Iniciando túnel SSH Serveo.")
        try:
            self.logger.info(f"Executando comando: {self.ssh_command}")
            ssh_tunnel_process = subprocess.Popen(
                self.ssh_command,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
        except FileNotFoundError:
            self.logger.exception("Executável SSH não encontrado.")
            self.handler.exception(
                message="Executável SSH não encontrado.",
                exception=FileNotFoundError,
            )
        except OSError:
            self.logger.exception("Erro ao iniciar túnel SSH Serveo.")
            self.handler.exception(
                message="Erro ao iniciar túnel SSH Serveo.",
                exception=OSError,
            )
        else:
            self.logger.info(f"Túnel iniciado com PID: {ssh_tunnel_process.pid}")
            return ssh_tunnel_process

    def stop_tunnel(self, proc: subprocess.Popen) -> None:
        """Encerra o processo do túnel SSH Serveo."""
        self.logger.info(f"Encerrando túnel Serveo (PID: {proc.pid})...")
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
                self.logger.info("Túnel SSH Serveo encerrado com sucesso.")
            except subprocess.TimeoutExpired:
                proc.kill()
                self.logger.warning("Forçou encerramento do túnel SSH Serveo após timeout.")
        else:
            self.logger.info(f"Processo já finalizado (PID: {proc.pid}).")
