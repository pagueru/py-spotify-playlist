# py-spotify-playlist

[![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)](https://www.python.org/) [![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Flask](https://img.shields.io/badge/-flask-%23000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/) [![Spotify](https://img.shields.io/badge/-spotify-1DB954?style=flat&logo=spotify&logoColor=white)](https://developer.spotify.com/)

Autenticação, integração e automação de playlists no Spotify, utilizando Python e Flask. O objetivo é testar a criação de playlists no Spotify utilizando a API oficial, com autenticação OAuth e manipulação de dados via Python e Flask. O projeto também explora o uso do Serveo, um serviço de tunelamento que permite expor localmente a aplicação Flask para a internet, facilitando o recebimento de callbacks de autenticação do Spotify durante o desenvolvimento.

## Principais aprendizados

- **Flask**: Backend web para autenticação OAuth, callbacks e integração com a API do Spotify.
- **Spotipy**: Integração OAuth e manipulação de playlists via API.
- **Organização**: Estrutura modular, logging, validações e configuração via arquivos.

## Requisitos

- [Python](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Flask](https://flask.palletsprojects.com/)
- [Spotipy](https://spotipy.readthedocs.io/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Configuração do Projeto

1. Cadastre uma aplicação no [Spotify for Developers](https://developer.spotify.com/dashboard) para obter as credenciais:s
   - `SPOTIPY_CLIENT_ID` e `SPOTIPY_CLIENT_SECRET`: serão gerados ao criar a aplicação.
   - `SPOTIPY_REDIRECT_URI`: defina como `https://py-spotify-playlist.serveo.net/callback` (ou o domínio configurado no Serveo). Esse URI será usado para receber os callbacks de autenticação do Spotify.
   - Essas informações serão usadas no arquivo `.env` do projeto.

2. Clone o repositório do projeto:

    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd py-spotify-playlist
    ```

3. Crie o arquivo `.env` a partir do exemplo:

    ```bash
    cp .env.example .env
    ```

    Preencha as variáveis com os dados obtidos no Spotify Developers.

4. Configure o arquivo de settings:

    O arquivo `src/config/files/settings.yaml` pode ser editado para ajustar o domínio do Serveo. O subdomínio será usado para receber os callbacks de autenticação do Spotify.

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
