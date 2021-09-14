from django.test import TestCase

# Create your tests here.
import requests

head = {"Authorization": "Token e511973c6608601880b5ad648f73cfa9fb4ed5e5"}
r = requests.put("https://api.bladelist.gg/bot/status/712323581828136971/", headers=head, json={"verification_status": "UNBANNED", "reason": "shits", "moderator_id": "710434346435346482"})

print(r.text)