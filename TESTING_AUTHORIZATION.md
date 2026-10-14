# Post authorization regression

Scope: create requires login; edit/delete require login and ownership. The server controls the author. This is not a full security audit. Footer PR21 is separate.

Run with Django 3.2 and the repository requirements, a disposable SQLite database, local file storage and the in-memory email backend. No real accounts, production database, Cloudinary credentials or network calls are required for these tests. Use a test-only settings module outside production configuration:

```python
import os
os.environ['DATABASE_URL'] = 'sqlite:////tmp/build-a-blog-auth.sqlite3'
from devblog.settings import *
SECRET_KEY = 'synthetic-local-tests-only'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/tmp/build-a-blog-auth.sqlite3'}}
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'cloudinary_storage']
```

Put that module on PYTHONPATH and run:

```sh
DJANGO_SETTINGS_MODULE=auth_test_settings python manage.py test blog.test_post_permissions
```

Ten tests cover anonymous GET/POST, non-owner GET/POST, owner create/edit/delete, forged author/status fields, missing objects, GET-delete safety, and CSRF. Cloudinary URL rendering is mocked; uploads are not exercised. Tests use invented users/posts only. Before the repair the suite failed with ten assertion failures and one error across subtests. After the repair all ten passed. Independent QA must reproduce the result against the PR head before approval. No merge or deployment is authorized by this record.
