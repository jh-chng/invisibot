FROM ros:humble-ros-base-jammy

SHELL ["bash", "-c"]

WORKDIR /invisibot
COPY . .

# Install dependencies for hic_main
RUN apt update && apt install curl python3 iputils-ping -y
RUN curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py && \
    python3 ./get-pip.py 
RUN pip install --upgrade pip && \
    pip install wheel uvicorn pydantic fastapi
# RUN pip install  --ignore-installed -r requirement.txt

# Clean up apt install
RUN rm -rf /var/lib/apt/lists/*

CMD ["bash"]
