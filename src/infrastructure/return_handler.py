"""Método utilitário para manipulação de retornos de funções."""

from logging import ERROR, INFO, WARNING, Logger

from src.common.base.base_class import BaseClass
from src.infrastructure.logger import LoggerSingleton


class ReturnHandler(BaseClass):
    """Classe para manipular retornos de funções."""

    def __init__(self) -> None:
        """Inicializa o manipulador de retornos com um logger."""
        self.logger: Logger = LoggerSingleton.logger or LoggerSingleton.get_logger()
        """Logger singleton para registrar eventos e erros."""

    def message(self, message: str, *, level: int = INFO) -> str:
        """Retorna uma mensagem simples e registra conforme o nível."""
        try:
            if level not in {INFO, WARNING, ERROR}:
                msg = (
                    f"Nível de log inválido: {level}. "
                    "Use 'logger.INFO', 'logger.WARNING' ou 'logger.ERROR'."
                )
                self.logger.error(msg, stacklevel=2)
                return ValueError(msg)

            if level == INFO:
                self.logger.info(message, stacklevel=2)
                return message
            if level == WARNING:
                self.logger.warning(message, stacklevel=2)
                return message
            if level == ERROR:
                self.logger.error(message, stacklevel=2)
                return message
        except Exception:
            self.logger.exception(
                f"Ocorreu um erro ao registrar a mensagem: {message}", stacklevel=2
            )
            raise
        else:
            return message

    def exception(self, message: str, exception: Exception) -> Exception:
        """Registra uma exceção com uma mensagem e levanta a exceção."""
        self.logger.exception(message, stacklevel=2)
        raise exception(message)
