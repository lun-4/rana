rana
====

reverse engineering wakatime for fun

## how do

```
pipenv install
pipenv run hypercorn --access-log - rana.run:app --bind 0.0.0.0:8000
```

then use nginx and point at this at will or something
