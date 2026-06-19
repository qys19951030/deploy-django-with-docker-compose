from django.test import TestCase, override_settings
from django.conf import settings
from django.urls import reverse, resolve
from django.contrib.staticfiles.storage import staticfiles_storage


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

    def test_static_url_helper(self):
        from django.templatetags.static import static
        result = static('admin/css/base.css')
        self.assertTrue(result.startswith('/static/'))
        self.assertIn('admin/css/base.css', result)

    def test_media_url_helper(self):
        from django.core.files.storage import default_storage
        url = default_storage.url('test.txt')
        self.assertTrue(url.startswith('/media/'))
        self.assertIn('test.txt', url)


class StaticMediaUrlTests(TestCase):
    @override_settings(DEBUG=True)
    def test_media_route_exists_in_debug_mode(self):
        from django.urls import get_resolver
        from django.conf import settings
        from django.conf.urls.static import static as static_helper

        urlpatterns = static_helper(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        self.assertTrue(len(urlpatterns) > 0)
        self.assertEqual(urlpatterns[0].pattern.regex.pattern, r'^media/(?P<path>.*)$')

    def test_admin_staticfiles_url(self):
        self.assertTrue(
            staticfiles_storage.exists('admin/css/base.css'),
            "Django admin static files should be collectible"
        )
