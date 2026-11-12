FROM nvcr.io/nvidia/rapidsai/base:26.02-cuda12-py3.12
USER root
ENV MPLBACKEND=Agg PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends wget ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY environment/requirements.txt /tmp/course-requirements.txt
RUN /opt/conda/bin/python -m pip install -r /tmp/course-requirements.txt
WORKDIR /course
EXPOSE 8888
ENTRYPOINT ["/opt/conda/bin/python", "-m", "jupyterlab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
