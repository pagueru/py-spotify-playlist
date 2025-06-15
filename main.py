"""Ponto de entrada principal do app Flask e integração dos módulos."""

import logging
import os
import sys
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from flask import Flask, request
from flask_talisman import Talisman
from spotipy.exceptions import SpotifyException

from src.application.spotify_auth_handler import SpotifyAuthHandler
from src.config.constants import REQUIRED_ENV
from src.infrastructure.logger import LoggerSingleton
from src.infrastructure.return_handler import INFO, ReturnHandler
from src.infrastructure.serveo_tunnel_manager import ServeoTunnelManager

# Atribuição do logger
logger = LoggerSingleton.logger or LoggerSingleton.get_logger()

# Carrega variáveis de ambiente do arquivo .env
logger.info("Iniciando processo de carregamento de variáveis de ambiente.")
load_dotenv()

# # Verificação de variáveis obrigatórias
for var in REQUIRED_ENV:
    valor = os.getenv(var)
    if not valor:
        print(valor)
        logger.error(f"Variável de ambiente obrigatória não definida: {var}")
        sys.exit(1)
    logger.debug(f"Variável de ambiente '{var}' carregada com valor: {valor}")

# Inicializa aplicação Flask
logger.info("Inicializando aplicação Flask.")
app = Flask(
    __name__,
    template_folder="./src/templates",
    static_folder="./src/static",
    static_url_path="",
)

# Força HTTPS e adiciona headers de segurança
Talisman(app, force_https=True)

# Instancia os gerenciadores
logger.info("Instanciando ReturnHandler, SpotifyAuthHandler e ServeoTunnelManager.")
return_handler = ReturnHandler()
spotify_auth = SpotifyAuthHandler(return_handler)
# serveo_manager = ServeoTunnelManager(return_handler)

# Inicia o túnel Serveo ANTES do servidor Flask
# logger.info("Iniciando túnel Serveo antes do servidor Flask.")
# serveo_proc = serveo_manager.start_tunnel()
# if serveo_proc is not None:
#     logger.info(f"Processo do túnel Serveo iniciado (PID: {serveo_proc.pid}).")
# else:
#     logger.warning("Processo do túnel Serveo não foi iniciado corretamente.")


@app.after_request
def apply_csp(response: str) -> str:
    """Aplica Content Security Policy (CSP) para segurança adicional."""
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'"
    return response


@app.route("/")
def route_login() -> str:
    """Rota inicial: inicia o fluxo de autenticação do usuário com o Spotify."""
    logger.info("Rota '/' acessada. Iniciando fluxo de login do usuário.")
    return spotify_auth.login()


@app.route("/callback")
def route_callback() -> str:
    """Rota de callback: recebe resposta do Spotify e cria a playlist."""
    logger.info("Rota '/callback' acessada. Processando callback do Spotify.")
    try:
        return spotify_auth.callback()
    except SpotifyException:
        return_handler.exception(
            message="Erro inesperado no callback do Spotify.",
            exception=Exception,
        )


try:
    logger.info(
        "Iniciando servidor Flask na porta 8888, aceitando conexões de todas as interfaces."
    )
    app.run(port=8888)
except KeyboardInterrupt:
    logger.info("Interrupção recebida. Encerrando servidor Flask e túnel Serveo...")
finally:
    # if serveo_proc is not None:
    #     logger.info(f"Encerrando túnel Serveo (PID: {serveo_proc.pid}).")
    #     serveo_manager.stop_tunnel(serveo_proc)
    logger.info("Aplicação finalizada.")
    sys.exit(0)
