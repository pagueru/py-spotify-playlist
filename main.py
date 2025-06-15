"""Ponto de entrada principal do app Flask e integração dos módulos."""

import logging
import os
import sys

from dotenv import load_dotenv
from flask import Flask

from src.application.spotify_auth_handler import SpotifyAuthHandler
from src.infrastructure.return_handler import INFO
from src.infrastructure.serveo_tunnel_manager import ServeoTunnelManager

# Configuração básica do logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(module)s:%(lineno)03d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Verificação de variáveis obrigatórias
required_env = ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI"]
for var in required_env:
    if not os.getenv(var):
        logger.error(f"Variável de ambiente obrigatória não definida: {var}")
        sys.exit(1)

logger.info("Iniciando o app...")

# Inicializa aplicação Flask
app = Flask(__name__)

# Instancia os gerenciadores
spotify_auth = SpotifyAuthHandler(logger)
serveo_manager = ServeoTunnelManager(logger)


@app.route("/")
def route_login() -> str:
    """Rota inicial: inicia o fluxo de autenticação do usuário com o Spotify."""
    return spotify_auth.login()


@app.route("/callback")
def route_callback() -> str:
    """Rota de callback: recebe resposta do Spotify e cria a playlist."""
    return spotify_auth.callback()


if __name__ == "__main__":
    serveo_proc = serveo_manager.start_tunnel()
    try:
        app.run(port=8888)
    except KeyboardInterrupt:
        logger.info("Interrupção recebida. Encerrando servidor Flask e túnel Serveo...")
    finally:
        serveo_manager.stop_tunnel(serveo_proc)
        logger.info("Aplicação finalizada.")
        sys.exit(0)
