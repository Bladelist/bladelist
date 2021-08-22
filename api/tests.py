from django.test import TestCase

# Create your tests here.
import requests

r = requests.get("http://api.blade.co:8000/bots/", headers={"Authorization": "Token 09dfa7bead7b4e57631559354c74f9734dc32715"})
print(r.text)