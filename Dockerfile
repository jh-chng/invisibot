FROM python:3.10.10

SHELL ["bash", "-c"]

# Set up workspace and all relevant files
WORKDIR /invisibot_ws
COPY requirements.txt requirements.txt

# Install python3 dependencies
RUN pip3 install -r requirements.txt

# Copy in invisibot source
COPY invisibot.py invisibot.py
COPY utils/ utils/

CMD ["bash"]