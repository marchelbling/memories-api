# Cultural data crawler

## Supported data
Supports crawling for:

* tv shows (themoviedb)
* movies (themoviedb)
* comics (bedetheque)

## CLI

```bash
for year in {1950..2016};
do
    PYTHONPATH=../.. python memories.py --tv --year ${year} >>/data/tvs.log
done
```
