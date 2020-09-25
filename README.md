# MobileSDWAN_Backend

Mobile SDWAN Solution:

Cisco ASA + Cisco NSO + Cisco SDWAN = Mobile SDWAN solution

This is the backend Server for Mobile SDWAN,

it consist of two parts, the NSO service module and the Python backend.

## Install
```bash
# Under NSO work dir.
cp THISPROJECTPATH/asauser ./packages/
cd ./packages/asauser/src/
make all
```

Install Python Backend:
```bash
pip install -r requirements.txt
mv config.yaml.example config.yaml
vi config.yaml
# Modify the NSO info to fit your environment
# Also modify the ASAServer IP to fit correct server.
# Then run
python3 ./main.py
```
And your server will be running at 9888 port.

Please modify Nginx to proxy_pass the backend request to Backend server.

