# Builder layer
FROM weboftrust/keri.base:arm64

WORKDIR /kourier

RUN python -m venv venv

ENV PATH=/kourier/venv/bin:${PATH}

RUN pip install --upgrade pip

# Copy Python dependency files in
COPY dist/kourier-0.0.1.tar.gz ./
# Set up Rust environment and install Python dependencies
# Must source the Cargo environment for the blake3 library to see
# the Rust intallation during requirements install
RUN . ${HOME}/.cargo/env && \
    pip install kourier-0.0.1.tar.gz

ENTRYPOINT [ "kourier" ]
