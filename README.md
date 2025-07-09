# **What Is This?**

This is a `HTTP` server running a simulated robot, that is useful for testing Open-RMF among other things.

# **Dependencies**
- python
- pip

# **Build**
```
python3 -m venv env
source ./env/bin/activate
pip install uvicorn pydantic fastapi
```
# **Run**
```
python3 -m invisibot
```
### **Verify**

Access endpoints on http://localhost:8080/docs