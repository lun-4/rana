rana
====

reverse engineering wakatime for fun

## how do

 - python 3.7
 - pipenv (`python3 -m pip install -U pipenv`)
 - sqlite

note: this is rudimentary software. db migrations, if required, won't
be automatic.

```bash
pipenv install

# you can put any port really i wont force you
pipenv run hypercorn --access-log - rana.run:app --bind 0.0.0.0:8000
```

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

## how to link editors to your rana instance

if you have the wakatime editor cli installed, you can fork/modify it, the point
of interest is `wakatime/api.py`. replace `api.wakatime.com` to your instance's
url as you want.

for vim-wakatime, as it embeds the entire wakatime cli with itself, you may
need to modify the plugin directly. an example is
https://gitdab.com/luna/vim-rana (points to localhost for testing)

for example, to repoint it to `rana.discordapp.io`:
```patch
diff --git a/packages/wakatime/api.py b/packages/wakatime/api.py
index 16286a4..546f693 100644
--- a/packages/wakatime/api.py
+++ b/packages/wakatime/api.py
@@ -49,7 +49,7 @@ def send_heartbeats(heartbeats, args, configs, use_ntlm_proxy=False):

     api_url = args.api_url
     if not api_url:
-        api_url = 'https://api.wakatime.com/api/v1/users/current/heartbeats.bulk'
+        api_url = 'https://rana.discordapp.io/api/v1/users/current/heartbeats.bulk'
     log.debug('Sending heartbeats to api at %s' % api_url)
     timeout = args.timeout
     if not timeout:
@@ -171,7 +171,7 @@ def get_time_today(args, use_ntlm_proxy=False):
     fetch summary.
     """

-    url = 'https://api.wakatime.com/api/v1/users/current/summaries'
+    url = 'https://rana.discordapp.io/api/v1/users/current/summaries'
     timeout = args.timeout
     if not timeout:
         timeout = 60
```
