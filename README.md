rana
====

reverse engineering wakatime for fun

## how do

 - python 3.7
 - pipenv (`python3 -m pip install -U pipenv`)
 - postgresql

note: this is rudimentary software. db migrations, if required, won't
be automatic.

```bash
pipenv install

# db setup can be so different between postgresql installations.
# db credentials go to config.ini
cp config.example.ini config.ini

# you can put any port really i wont force you
pipenv run hypercorn --access-log - rana.run:app --bind 0.0.0.0:8000
```

*todo: configuration of instances (e.g disable signups)*

then nginx or something

```nginx
server {
    # i wont put tls/ssl stuff here since that can change and be
    # different from deploy to deploy.

    listen 80;
    server_name uwu.com;

    location / {
            proxy_set_header Host $http_host;
            proxy_pass http://localhost:8000;
    }
}
```

### api keys

your wakatime API keys won't work on a rana instance. go to
`instance.tld/signup` to well, signup. then login via `/login`, api keys are
displayed on dashboard.

there is no "recover account" or update username mechanism as of right now.

## how to link editors to your rana instance

if you're on vim: https://gitdab.com/lavatech/vim-rana is the plugin for you.
go to your `~/.wakatime.cfg` file, replace `api_key`, and add `base_url`
pointing to, for example, `https://rana.instance.tld`.

if you're not but you still have the wakatime cli python program installed, you
*can* modify it to point to your preffered rana instance. the vim-rana plugin
contains a modified wakatime cli. there isn't a fork yet because of the burden
of keeping modifications in sync between the repositories.
