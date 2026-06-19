from django.test import TestCase, override_settings
from django.conf import settings
from django.contrib.staticfiles import finders


class StaticMediaSettingsTests(TestCase):
    def test_static_url_configuration(self):
        self.assertEqual(settings.STATIC_URL, '/static/')

    def test_media_url_configuration(self):
        self.assertEqual(settings.MEDIA_URL, '/media/')

    def test_static_root_configuration(self):
        self.assertEqual(settings.STATIC_ROOT, '/vol/web/static')

    def test_media_root_configuration(self):
        self.assertEqual(settings.MEDIA_ROOT, '/vol/web/media')

    def test_no_nested_static_url(self):
        self.assertNotIn('/static/static/', settings.STATIC_URL)
        self.assertNotIn('/static/media/', settings.MEDIA_URL)
        self.assertNotEqual(settings.STATIC_URL, '/static/static/')
        self.assertNotEqual(settings.MEDIA_URL, '/static/media/')

    def test_static_url_helper(self):
        from django.templatetags.static import static
        result = static('admin/css/base.css')
        self.assertEqual(result, '/static/admin/css/base.css')

    def test_media_url_helper(self):
        from django.core.files.storage import default_storage
        url = default_storage.url('test.txt')
        self.assertEqual(url, '/media/test.txt')

    def test_staticfiles_finders_configured(self):
        self.assertIn(
            'django.contrib.staticfiles.finders.AppDirectoriesFinder',
            settings.STATICFILES_FINDERS
        )

    def test_admin_staticfiles_discoverable(self):
        found = finders.find('admin/css/base.css')
        self.assertIsNotNone(
            found,
            "admin/css/base.css should be discoverable via staticfiles finders"
        )
        normalized = found.replace('\\', '/')
        self.assertTrue(normalized.endswith('admin/css/base.css'))


class StaticMediaUrlTests(TestCase):
    @override_settings(DEBUG=True)
    def test_debug_mode_media_route(self):
        from django.conf import settings
        from django.conf.urls.static import static as static_helper

        urlpatterns = static_helper(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        self.assertEqual(len(urlpatterns), 1)
        self.assertEqual(
            urlpatterns[0].pattern.regex.pattern,
            r'^media/(?P<path>.*)$'
        )

    @override_settings(DEBUG=True)
    def test_debug_mode_static_route(self):
        from django.conf import settings
        from django.conf.urls.static import static as static_helper

        urlpatterns = static_helper(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        self.assertEqual(len(urlpatterns), 1)
        self.assertEqual(
            urlpatterns[0].pattern.regex.pattern,
            r'^static/(?P<path>.*)$'
        )

    @override_settings(DEBUG=True)
    def test_urlconf_has_media_route_when_debug_enabled(self):
        import importlib
        from django.conf import settings
        import app.urls

        importlib.reload(app.urls)
        urlpatterns = app.urls.urlpatterns

        has_media_route = False
        for pattern in urlpatterns:
            if (hasattr(pattern, 'pattern') and
                    hasattr(pattern.pattern, 'regex') and
                    pattern.pattern.regex.pattern == r'^media/(?P<path>.*)$'):
                has_media_route = True
                break
        self.assertTrue(
            has_media_route,
            "MEDIA route should be present in urlpatterns when DEBUG=True"
        )
