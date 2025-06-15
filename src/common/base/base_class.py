"""Módulo base para todas as classes do projeto."""

from dataclasses import dataclass, field
import inspect
from logging import Logger
from pathlib import Path
import shutil
from typing import Any

import yaml

from src.common.echo import echo
from src.common.errors.errors import ProjectError
from src.config.constypes import PathLike


@dataclass
class BaseClass:
    """Classe base para fornecer métodos comuns a todas as classes."""

    logger: Logger = field(init=False)
    """Logger singleton para registrar eventos e erros."""

    def _handle_error(self, exception: type[Exception] = ProjectError, message: str = "") -> None:
        """Lida com erros lançando uma exceção personalizada e registrando a mensagem de erro."""
        self.logger.error(message)
        raise exception(message)

    def _handle_exception(
        self, exception: type[Exception] = ProjectError, message: str = ""
    ) -> None:
        """Lida com exceções lançando uma exceção personalizada e registrando a mensagem de erro."""
        self.logger.exception(message)
        raise exception(message)

    def _separator_line(self, char: str = "-", padding: int = 0) -> None:
        """Imprime uma linha ajustada ao tamanho do terminal ou ao valor fornecido pelo usuário."""
        try:
            width = padding if padding > 0 else shutil.get_terminal_size((80, 20)).columns
            print(char * width)
        except OSError:
            self._handle_exception(ProjectError, "Falha ao obter o tamanho do terminal.")

    def _ensure_path(self, path_str: PathLike) -> Path:
        """Converte uma string de caminho em um objeto Path e garante que o diretório exista."""
        if not isinstance(path_str, (str, Path)):
            msg = "O caminho deve ser uma string ou um objeto Path."
            echo(msg, "error")
            raise ProjectError(msg)
        path: Path = Path(path_str)
        if not path.parent.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except ProjectError as e:
                echo(f"Erro ao criar diretório: {e}", "error")
                raise
        return path
