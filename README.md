memories (falcon) api: [instant] search
============================

```bash

docker build -t mrchlblng/memories-api .
docker run --rm -v /data:/data -p 8000:8000 mrchlblng/memories-api > /var/log/memories/gunicorn.log 2>&1 &
curl http://serverip:8000/search
```


## Configuration

A `config.rc` file should be found in any folder (best in the root folder). Structure needed:

```
[memories]
storage: <DB STORAGE PATH>
db_name: <SQLITE DB FILENAME>
[themoviedb]
token: <THEMOVIEDB API TOKEN>
```
