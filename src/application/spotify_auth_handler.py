"""Classe utilitária para autenticação e integração com o Spotify."""

import os
from typing import TYPE_CHECKING

from flask import redirect, render_template, request
from jinja2.exceptions import TemplateError
from requests.exceptions import HTTPError
import spotipy
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from src.common.base.base_class import BaseClass
from src.infrastructure.logger import LoggerSingleton
from src.infrastructure.return_handler import ERROR, INFO, WARNING, ReturnHandler

if TYPE_CHECKING:
    from logging import Logger


class SpotifyAuthHandler:
    """Gerencia o fluxo de autenticação e criação de playlists no Spotify."""

    def __init__(self, return_handler: ReturnHandler) -> None:
        """Inicializa o handler de autenticação do Spotify."""
        self.logger: Logger = LoggerSingleton.logger or LoggerSingleton.get_logger()
        """Logger singleton para registrar eventos e erros."""

        self.handler = return_handler
        """Instancia do ReturnHandler para gerenciar mensagens de retorno."""

        self.scope = "playlist-modify-public"
        """Define o escopo de permissão para modificar playlists públicas."""

        self.spotify_oauth = self._load_spotify_oauth()
        """Inicializa o SpotifyOAuth com as variáveis de ambiente necessárias."""

    def login(self) -> str:
        """Inicia o fluxo de autenticação do usuário com o Spotify."""
        self.logger.info("Iniciando fluxo de login do usuário.")
        auth_url = self.spotify_oauth.get_authorize_url()
        self.logger.info(f"URL de autenticação gerada: {auth_url}")
        return redirect(auth_url)

    def callback(self) -> str:
        """Recebe o callback do Spotify após autenticação e cria uma playlist."""
        self.logger.info("Recebida requisição de callback do Spotify.")
        code = request.args.get("code")
        error = request.args.get("error")

        if error:
            return self._handle_error(f"Erro na autenticação do Spotify: {error}", error)
        if not code:
            return self._handle_error(
                "Nenhum código de autorização recebido.",
                "Nenhum código de autorização recebido.",
                warning=True,
            )

        token_info = self._get_token_info(code)
        if not token_info or token_info.get("access_token") is None:
            self.handler.message(
                message="Token de acesso não foi obtido.",
                level=ERROR,
            )
            return redirect(self.spotify_oauth.get_authorize_url())

        playlist_url, error_msg = self._create_playlist(token_info["access_token"])
        return self._render_playlist_template(playlist_url, error_msg)

    def _handle_error(self, log_message: str, error_msg: str, *, warning: bool = False) -> str:
        """Registra e retorna erro renderizando o template apropriado."""
        level = WARNING if warning else ERROR
        self.handler.message(message=log_message, level=level)
        return render_template("error.html", error=error_msg)

    def _get_token_info(self, code: str) -> dict | None:
        """Obtém o token de acesso do Spotify."""
        try:
            return self.spotify_oauth.get_access_token(code)
        except HTTPError:
            self.handler.exception(
                message="Erro ao obter token de acesso do Spotify.",
                exception=HTTPError,
            )

    def _create_playlist(self, access_token: str) -> tuple[str | None, str | None]:
        """Cria uma playlist para o usuário autenticado e retorna a URL ou mensagem de erro."""
        try:
            spotify_client = spotipy.Spotify(auth=access_token)
            user = spotify_client.current_user()
            if "id" not in user:
                return None, self.handler.message(
                    message="Resposta do Spotify não contém o ID do usuário.",
                    level=ERROR,
                )
            user_id = user["id"]
            self.logger.info(f"Usuário autenticado: {user_id}")
            playlist = spotify_client.user_playlist_create(
                user=user_id, name="Minha Playlist via Serveo", public=True
            )
            if (
                not playlist
                or "id" not in playlist
                or "external_urls" not in playlist
                or "spotify" not in playlist["external_urls"]
            ):
                return None, self.handler.message(
                    message="Resposta do Spotify não contém informações completas da playlist.",
                    level=ERROR,
                )
            self.logger.info(f"Playlist criada com sucesso: {playlist['id']}")
            return playlist["external_urls"]["spotify"], None
        except SpotifyException:
            self.handler.exception(
                message="Erro ao criar playlist no Spotify.",
                exception=SpotifyException,
            )
        except KeyError:
            self.handler.exception(
                message="Erro ao acessar chave obrigatória.",
                exception=KeyError,
            )

    def _render_playlist_template(self, playlist_url: str | None, error_msg: str | None) -> str:
        """Renderiza o template de playlist ou de erro."""
        try:
            self.logger.info("Renderizando template de playlist.")
            if error_msg:
                return render_template("error.html", error=error_msg)
            return render_template("playlist.html", playlist_url=playlist_url)
        except (TemplateError, KeyError) as e:
            self.handler.exception(
                message="Erro ao renderizar template.",
                exception=type(e),
            )

    def _load_spotify_oauth(self) -> SpotifyOAuth:
        """Carrega e valida as variáveis de ambiente para o SpotifyOAuth."""
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
        missing = []
        if not client_id:
            missing.append("SPOTIPY_CLIENT_ID")
        if not client_secret:
            missing.append("SPOTIPY_CLIENT_SECRET")
        if not redirect_uri:
            missing.append("SPOTIPY_REDIRECT_URI")
        if missing:
            msg = f"Variáveis de ambiente ausentes: {', '.join(missing)}"
            self.logger.error(msg)
            self.handler.exception(message=msg, exception=OSError)
        try:
            return SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=self.scope,
            )
        except Exception as exc:
            self.handler.exception(
                message=f"Erro ao inicializar SpotifyOAuth: {exc}",
                exception=type(exc),
            )
            raise
