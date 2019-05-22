rana
====

reverse engineering wakatime for fun

## notes

there is no timezone gathering, this decision is intentional. all times
displayed in the API are in UTC.

## how do

```
pipenv install
pipenv run hypercorn --access-log - rana.run:app --bind 0.0.0.0:8000
```

then use nginx and point at this at will or something
