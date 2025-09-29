import os
import sys

# Adjust to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Use dev settings like manage.py did
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_invite.settings.dev')

import django
django.setup()

from django.test import Client

client = Client()

token = '3c9e4f00-492a-4911-843e-1b10aa07ad40'
path = f'/invitations/detail/{token}/'
print('Requesting', path)
resp = client.get(path, SERVER_NAME='localhost', HTTP_HOST='localhost')
print('Status code:', resp.status_code)
print('Content length:', len(resp.content))
# detect if splash overlay exists in HTML
has_splash_html = b'id="splashOverlay"' in resp.content
print('splashOverlay present in HTML:', has_splash_html)
# detect shouldShow variable in the JS
has_shouldshow = b'const shouldShow =' in resp.content
print('JS contains shouldShow var:', has_shouldshow)
if has_shouldshow:
    # extract the line
    idx = resp.content.find(b'const shouldShow =')
    snippet = resp.content[idx: idx+60]
    print('shouldShow snippet:', snippet.decode('utf-8', errors='replace'))

# Now simulate accepting the invitation via respond endpoint
respond_url = f'/invitations/respond/{token}/'
print('\nPosting RSVP accept to', respond_url)
post_resp = client.post(respond_url, {'invitation_status': 'accepted'}, SERVER_NAME='localhost', HTTP_HOST='localhost', follow=True)
print('POST status:', post_resp.status_code)
print('Final URL after follow:', post_resp.redirect_chain[-1][0] if post_resp.redirect_chain else 'no redirects')

# Fetch invite detail again
resp2 = client.get(path, SERVER_NAME='localhost', HTTP_HOST='localhost')
print('\nAfter accept - Status code:', resp2.status_code)
print('Content length:', len(resp2.content))
print('splashOverlay present after accept:', b'id="splashOverlay"' in resp2.content)
print('JS contains shouldShow var after accept:', b'const shouldShow =' in resp2.content)
if b'const shouldShow =' in resp2.content:
    idx = resp2.content.find(b'const shouldShow =')
    snippet = resp2.content[idx: idx+60]
    print('shouldShow snippet after accept:', snippet.decode('utf-8', errors='replace'))
