# **What Is This?**

This is a **lightweight** `HTTP` server running **a simulated robot**, that is useful for testing [Open-RMF](https://www.open-rmf.org/) without reliance on hardware availability and reliability.

# **Dependencies** 📚
- python
- pip

# **Build** 🔨

```bash
git clone https://github.com/jh-chng/invisibot.git --depth 1 --single-branch --branch main && cd invisibot
```

```bash
python3 -m venv env
```

```bash
source env/bin/activate
```

```bash
pip install -r requirements.txt
```

# **Run** ⚙️

```
python3 -m invisibot
```

### **Verify** ✅

Access endpoints on http://localhost:8080/docs.

You should see something similar to what is shown below:
![](img/swagger_ui.png)

### **Maintainer(s)** 👓

- [jn-chng](https://github.com/jh-chng)
- [cardboardcode](https://github.com/cardboardcode)