# SOREX_test
```
usage: docker-compose up --build -d
```
TELEGRAM_TOKEN and COINMARKETCAP_TOKEN must be provided in .env.

While building you may issue troubles while `pip install` step, try:  
`nano /etc/docker/daemon.json`  
Paste in file:  
{  
&nbsp;&nbsp;&nbsp;&nbsp;"mtu": 1400  
}  
`sudo systemctl restart docker`
source: https://stackoverflow.com/a/75452499