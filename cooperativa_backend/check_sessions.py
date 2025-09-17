import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
django.setup()

from django.contrib.sessions.models import Session

print('Active sessions:')
sessions = Session.objects.all()
print(f'Total sessions: {sessions.count()}')

for s in sessions[:5]:
    try:
        decoded = s.get_decoded()
        print(f'Session {s.session_key}: {decoded}')
    except Exception as e:
        print(f'Session {s.session_key}: Error decoding - {e}')