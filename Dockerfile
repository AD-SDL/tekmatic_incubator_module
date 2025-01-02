FROM ghcr.io/ad-sdl/wei

# TODO: update labels, if neccessary
LABEL org.opencontainers.image.source=https://github.com/AD-SDL/tekmatic_incubator_module
LABEL org.opencontainers.image.description="A template python module that demonstrates basic WEI module functionality."
LABEL org.opencontainers.image.licenses=MIT

#########################################
# Module specific logic goes below here #
#########################################

RUN mkdir -p tekmatic_incubator_module

COPY ./src tekmatic_incubator_module/src
COPY ./README.md tekmatic_incubator_module/README.md
COPY ./pyproject.toml tekmatic_incubator_module/pyproject.toml

RUN --mount=type=cache,target=/root/.cache \
    pip install ./tekmatic_incubator_module

# TODO: Add any device-specific container configuration/setup here

CMD ["python", "tekmatic_incubator_module.py"]

#########################################
