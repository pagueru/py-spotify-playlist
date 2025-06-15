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
from src.config.constants import APP_TEMPLATE
from src.infrastructure.logger import LoggerSingleton
from src.infrastructure.return_handler import ERROR, INFO, WARNING, ReturnHandler

if TYPE_CHECKING:
    from logging import Logger


class SpotifyAuthHandler(BaseClass):
    """Gerencia o fluxo de autenticação e criação de playlists no Spotify."""

    def __init__(self, return_handler: ReturnHandler) -> None:
        """Inicializa o handler de autenticação do Spotify."""
        self.logger: Logger = LoggerSingleton.logger or LoggerSingleton.get_logger()
        self.logger.info("Inicializando handler com ReturnHandler.")
        self.handler = return_handler
        self.scope = "playlist-modify-public"
        self.logger.info(f"Escopo definido: {self.scope}")
        self.spotify_oauth = self._load_spotify_oauth()
        self.logger.info("SpotifyAuthHandler inicializado com sucesso.")

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
        self.logger.info(f"Parâmetros recebidos: code={code}, error={error}")

        if error:
            self.logger.warning(f"Erro recebido do Spotify: {error}")
            return self._handle_error(f"Erro na autenticação do Spotify: {error}", error)
        if not code:
            self.logger.warning("Nenhum código de autorização recebido.")
            return self._handle_error(
                "Nenhum código de autorização recebido.",
                "Nenhum código de autorização recebido.",
                warning=True,
            )

        token_info = self._get_token_info(code)
        self.logger.info(f"Token info obtido: {token_info}")
        if not token_info or token_info.get("access_token") is None:
            self.logger.error("Token de acesso não foi obtido.")
            self.handler.message(
                message="Token de acesso não foi obtido.",
                level=ERROR,
            )
            return redirect(self.spotify_oauth.get_authorize_url())

        playlist_url, error_msg = self._create_playlist(token_info["access_token"])
        self.logger.info(f"Playlist URL: {playlist_url}, error_msg: {error_msg}")
        return self._render_playlist_template(playlist_url, error_msg)

    def _handle_error(self, log_message: str, error_msg: str, *, warning: bool = False) -> str:
        """Registra e retorna erro renderizando o template apropriado."""
        level = WARNING if warning else ERROR
        self.logger.log(level, f"{log_message}")
        self.handler.message(message=log_message, level=level)
        return render_template("error.html", error=error_msg)

    def _get_token_info(self, code: str) -> dict | None:
        """Obtém o token de acesso do Spotify."""
        self.logger.info(f"Obtendo token para code: {code}")
        try:
            token = self.spotify_oauth.get_access_token(code)
            self.logger.info(f"Token recebido: {token}")
        except HTTPError:
            self.logger.exception("Erro ao obter token de acesso")
            self.handler.exception(
                message="Erro ao obter token de acesso do Spotify.",
                exception=HTTPError,
            )
        else:
            return token

    def _create_playlist(self, access_token: str) -> tuple[str | None, str | None]:
        """Cria uma playlist para o usuário autenticado e retorna a URL ou mensagem de erro."""
        self.logger.info(f"Criando playlist com access_token: {access_token[:8]}... (ocultado)")
        try:
            spotify_client = spotipy.Spotify(auth=access_token)
            user = spotify_client.current_user()
            self.logger.info(f"Usuário retornado: {user}")
            if "id" not in user:
                self.logger.error("Resposta do Spotify não contém o ID do usuário.")
                return None, self.handler.message(
                    message="Resposta do Spotify não contém o ID do usuário.",
                    level=ERROR,
                )
            user_id = user["id"]
            self.logger.info(f"Usuário autenticado: {user_id}")
            playlist = spotify_client.user_playlist_create(
                user=user_id, name="Minha Playlist via Serveo", public=True
            )
            self.logger.info(f"Playlist retornada: {playlist}")
            if (
                not playlist
                or "id" not in playlist
                or "external_urls" not in playlist
                or "spotify" not in playlist["external_urls"]
            ):
                self.logger.error(
                    "Resposta do Spotify não contém informações completas da playlist."
                )
                return None, self.handler.message(
                    message="Resposta do Spotify não contém informações completas da playlist.",
                    level=ERROR,
                )
            self.logger.info(f"Playlist criada com sucesso: {playlist['id']}")
            return playlist["external_urls"]["spotify"], None
        except SpotifyException:
            self.logger.exception("Erro ao criar playlist no Spotify.")
            self.handler.exception(
                message="Erro ao criar playlist no Spotify.",
                exception=SpotifyException,
            )
        except KeyError:
            self.logger.exception("Erro ao acessar chave obrigatória.")
            self.handler.exception(
                message="Erro ao acessar chave obrigatória.",
                exception=KeyError,
            )

    def _render_playlist_template(self, playlist_url: str | None, error_msg: str | None) -> str:
        """Renderiza o template de playlist ou de erro."""
        self.logger.info(
            f"Renderizando template. playlist_url={playlist_url}, error_msg={error_msg}"
        )
        try:
            if error_msg:
                self.logger.warning(f"Renderizando template de erro: {error_msg}")
                return render_template("error.html", error=error_msg)
            self.logger.info("Renderizando template do app com playlist_url.")
            # APP_TEMPLATE agora é uma string com o nome do template (ex: 'app.html')
            return render_template(APP_TEMPLATE, playlist_url=playlist_url)
        except (TemplateError, KeyError):
            self.logger.exception("Erro ao renderizar template.")
            self.handler.exception(
                message="Erro ao renderizar template.",
                exception=TemplateError,
            )

    def _load_spotify_oauth(self) -> SpotifyOAuth:
        """Carrega e valida as variáveis de ambiente para o SpotifyOAuth."""
        self.logger.info("Carregando variáveis de ambiente do Spotify.")
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
        self.logger.info(
            f"client_id={client_id}, "
            f"client_secret={'***' if client_secret else None}, redirect_uri={redirect_uri}"
        )
        missing = []
        if not client_id:
            missing.append("SPOTIPY_CLIENT_ID")
        if not client_secret:
            missing.append("SPOTIPY_CLIENT_SECRET")
        if not redirect_uri:
            missing.append("SPOTIPY_REDIRECT_URI")
        if missing:
            msg = f"Variáveis de ambiente ausentes: {', '.join(missing)}"
            self.logger.error(f"{msg}")
            self.handler.exception(message=msg, exception=OSError)
        try:
            self.logger.info("Inicializando SpotifyOAuth com as variáveis de ambiente.")
            return SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=self.scope,
            )
        except Exception:
            self.logger.exception("Erro ao inicializar SpotifyOAuth.")
            self.handler.exception(
                message="Erro ao inicializar SpotifyOAuth.",
                exception=OSError,
            )
            raise
