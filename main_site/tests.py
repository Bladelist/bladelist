from django.test import TestCase

# Create your tests here.
import requests

head = {"Authorization": "Token 09dfa7bead7b4e57631559354c74f9734dc32715"}
r = requests.put("http://api.blade.co:8000/bot/status/604230021594480650/", headers=head, json={"verification_status": "UNBANNED", "reason": "shits", "moderator_id": "710434346435346482"})

print(r.text)