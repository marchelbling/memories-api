memories (falcon) api: search
============================
```bash
docker build -t mrchlblng/memories-api .
docker run -v /data/memories:/searchdata -p 8000:8000 mrchlblng/memories-api
curl http://serverip:8000/search
```
