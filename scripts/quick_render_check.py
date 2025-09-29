# Quick render check for invite_detail and RSVP flow
import os
import sys

# Find project root (where manage.py exists)
this = os.path.abspath(os.path.dirname(__file__))
root = this
while not os.path.exists(os.path.join(root, 'manage.py')):
    parent = os.path.dirname(root)
    if parent == root:
        raise SystemExit('Could not find project root')
    root = parent

sys.path.insert(0, root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_invite.settings.dev')

import django  # noqa: E402
django.setup()  # noqa: E402

from django.test import Client  # noqa: E402

client = Client()

token = '3c9e4f00-492a-4911-843e-1b10aa07ad40'
path = f'/invitations/detail/{token}/'
print('Requesting', path)
resp = client.get(path, SERVER_NAME='localhost', HTTP_HOST='localhost')
print('Status code:', resp.status_code)
print('Content length:', len(resp.content))
print('splashOverlay present in HTML:', b'id="splashOverlay"' in resp.content)
# check for JS variable
print('contains shouldShowModal true:', b'const shouldShowModal = true' in resp.content)
print('contains shouldShowModal false:', b'const shouldShowModal = false' in resp.content)

respond_url = f'/invitations/respond/{token}/'
print('\nPosting RSVP accept to', respond_url)
post_resp = client.post(respond_url, {'invitation_status': 'accepted'}, SERVER_NAME='localhost', HTTP_HOST='localhost', follow=True)
print('POST status:', post_resp.status_code)
print('Redirect chain:', post_resp.redirect_chain)

resp2 = client.get(path, SERVER_NAME='localhost', HTTP_HOST='localhost')
print('\nAfter accept - Status code:', resp2.status_code)
print('contains ?profile_modal in previous redirect (last redirect URL):', post_resp.redirect_chain[-1][0] if post_resp.redirect_chain else '')
print('Now contains shouldShowModal true:', b'const shouldShowModal = true' in resp2.content)
print('Now contains shouldShowModal false:', b'const shouldShowModal = false' in resp2.content)
