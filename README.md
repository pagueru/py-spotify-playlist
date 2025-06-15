# py-spotify-playlist

Automatização do processo de autenticação e criação de playlists no Spotify via integração web, utilizando Flask e Spotipy.

[![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)](https://www.python.org/) [![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Flask](https://img.shields.io/badge/-flask-%23000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/) [![Spotify](https://img.shields.io/badge/-spotify-1DB954?style=flat&logo=spotify&logoColor=white)](https://developer.spotify.com/)

## Sobre o Projeto

Autenticação, integração e automação de playlists no Spotify, utilizando Python e Flask. O objetivo é testar a criação de playlists no Spotify utilizando a API oficial, com autenticação OAuth e manipulação de dados via Python e Flask. O projeto também explora o uso do Serveo, um serviço de tunelamento que permite expor localmente a aplicação Flask para a internet, facilitando o recebimento de callbacks de autenticação do Spotify durante o desenvolvimento.

### Principais aprendizados

- **Flask**: Backend web para autenticação OAuth, callbacks e integração com a API do Spotify.
- **Spotipy**: Integração OAuth e manipulação de playlists via API.
- **Organização**: Estrutura modular, logging robusto e configuração via arquivos.
- **Boas Práticas**: Tipagem forte, validações, linting com Ruff e logging estruturado.

## Requisitos

- [Python](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Flask](https://flask.palletsprojects.com/)
- [Spotipy](https://spotipy.readthedocs.io/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Configuração do Projeto

1. Clone o repositório do projeto:

    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd py-spotify-playlist
    ```

2. Crie o arquivo `.env` a partir do exemplo:

    ```bash
    cp .env.example .env
    ```

    Preencha as variáveis `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET` e `SPOTIPY_REDIRECT_URI` com seus dados do Spotify.

3. Configure o arquivo de settings:

    Edite `src/config/files/settings.yaml` conforme necessário para ajustar logs e domínio do Serveo.

## Instalação

Instalação recomendada (usando `uv`):

```bash
uv sync --all-extras
```

Alternativamente, instale as dependências via `pip`:

```bash
pip install -r requirements.txt
```

## Execução

Execute o app localmente:

```bash
uv run main.py
```

Abra um terminal separado e execute o comando abaixo para expor sua aplicação local usando o Serveo. O nome do subdomínio será gerado conforme configurado em `src/config/files/settings.yaml` (campo `serveo.domain`):

```bash
ssh -R py-spotify-playlist:80:localhost:8888 serveo.net
```

- Acesse a URL gerada pelo Serveo no navegador para iniciar o fluxo de autenticação.
- Após a autenticação, uma página web minimalista será exibida confirmando a criação bem-sucedida da playlist.

## Contato

GitHub: [pagueru](https://github.com/pagueru/)

LinkedIn: [Raphael Coelho](https://www.linkedin.com/in/raphaelhvcoelho/)

E-mail: [raphael.phael@gmail.com](mailto:raphael.phael@gmail.com)
