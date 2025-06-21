FROM mcr.microsoft.com/vscode/devcontainers/python:3.12 as base
FROM ghcr.io/astral-sh/uv:latest as uv
FROM base
COPY --from=uv /uv /bin/uv
COPY --from=uv /uvx /bin/uvx
ENV UV_LINK_MODE=copy
