memories (falcon) api: [instant] search
============================
```bash

docker build -t mrchlblng/memories-api .
docker run -v /data:/data -p 8000:8000 mrchlblng/memories-api
curl http://serverip:8000/search
```
