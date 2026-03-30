from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings

from germanium.tools import assert_raises

from security.throttling.exception import ThrottlingException
from security.throttling.validators import PerRequestCacheThrottlingValidator


class PerRequestCacheThrottlingValidatorTestCase(TestCase):

    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def _make_request(self, path='/test/', method='GET', ip='127.0.0.1'):
        request = self.factory.generic(method, path)
        request.META['REMOTE_ADDR'] = ip
        return request

    @override_settings(SECURITY_THROTTLING_ENABLED=True)
    def test_over_limit_should_raise_throttling_exception(self):
        validator = PerRequestCacheThrottlingValidator(60, 2)
        request = self._make_request()
        validator.validate(request)
        validator.validate(request)
        with assert_raises(ThrottlingException):
            validator.validate(request)

    @override_settings(SECURITY_THROTTLING_ENABLED=True)
    def test_different_paths_should_be_throttled_independently(self):
        validator = PerRequestCacheThrottlingValidator(60, 2)
        request_a = self._make_request(path='/path-a/')
        request_b = self._make_request(path='/path-b/')
        validator.validate(request_a)
        validator.validate(request_a)
        validator.validate(request_b)
        validator.validate(request_b)
        with assert_raises(ThrottlingException):
            validator.validate(request_a)
