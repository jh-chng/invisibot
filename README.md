# Invisibot

This is a HTTP server running a simulated robot, that is useful for testing Open-RMF among other things. 
# Required dependencies
- python
- pip

# Install dependencies
```
python3 -m venv env
source ./env/bin/activate
pip install uvicorn pydantic fastapi
```
# Run
```
python3 -m invisibot
```
### Endpoints available
You can check out the endpoints on http://localhost:8080/docs