To install on your Umbrel, install ngrok, pipenv, and dependencies and create the following services:

- /etc/systemd/system/ngrok.service
- /etc/systemd/system/scenic-route.service

Make sure to enable the services:

```
sudo systemctl enable ngrok
sudo systemctl enable scenic-route
```

Next, install a cron job to re-populate the graph occasionally:

```
0 */6 * * * cd /home/umbrel/scenic-route && pipenv run ./refresh_graph
```


