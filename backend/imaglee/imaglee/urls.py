from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.decorators.csrf import csrf_exempt

from wagtail.core import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from imaglee.schema import schema
from graphene_django.views import GraphQLView


# Non-translatable URLs
#
    urlpatterns = [
        # Djnago 
        path('django-admin/', admin.site.urls), 
        
        # Wagtail
        path("admin/", include(wagtailadmin_urls)), 
        path("documents/", include(wagtaildocs_urls)),
        path("search/", search_views.search, name="search"),
        path('', include(wagtail_urls))
        re_path(r'^protected-media/(?P<path>.*)$', protected_media, name='protected_media'),
        
        # GraphQL
        path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=os.getenv('DEBUG', 'False') == 'True', schema=schema))),  # GraphQL endpoint
    ]


# Translatable URLs
#
    urlpatterns += i18n_patterns(
    )

