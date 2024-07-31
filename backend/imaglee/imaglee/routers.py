from django.conf import settings
from django.apps import apps

DEFAULT_APPS = [
	'auth', 
	'admin', 
	'sessions', 
	'contenttypes', 
	'sites',
	'flatpages', 
	'redirects', 
	'logentry'
]

class BaseRouter:
	def __init__(self, app_labels=None, db_name=None, exclude_labels=None):
		self.app_labels = app_labels or []
		self.db_name = db_name
		self.exclude_labels = exclude_labels or []

	def db_for_read(self, model, **hints):
		if self._should_route(model):
			return self.db_name
		return None

	def db_for_write(self, model, **hints):
		if self._should_route(model):
			return self.db_name
		return None

	def allow_relation(self, obj1, obj2, **hints):
		if self._should_route(obj1) or self._should_route(obj2):
			return True
		return None

	def allow_migrate(self, db, app_label, model_name=None, **hints):
		if app_label in self.app_labels and app_label not in self.exclude_labels:
			return db == self.db_name
		return None

	def _should_route(self, obj):
		app_label = obj._meta.app_config.name
		return app_label in self.app_labels and app_label not in self.exclude_labels

class WagtailRouter(BaseRouter):
	def __init__(self):
		super().__init__(app_labels=['app_wagtail'], db_name='db_wagtail')

class AppsRouter(BaseRouter):
	def __init__(self):
		super().__init__(exclude_labels=DEFAULT_APPS + ['app_wagtail'], db_name='db_apps')

class DjangoRouter(BaseRouter):
	def __init__(self):
		super().__init__(app_labels=DEFAULT_APPS, db_name='db_django')
