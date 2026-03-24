from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings

from germanium.tools import assert_false, assert_raises, assert_true

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
    def test_requests_under_limit_should_pass(self):
        validator = PerRequestCacheThrottlingValidator(60, 3)
        request = self._make_request()
        assert_true(validator._validate(request))
        assert_true(validator._validate(request))
        assert_true(validator._validate(request))

    @override_settings(SECURITY_THROTTLING_ENABLED=True)
    def test_requests_over_limit_should_fail(self):
        validator = PerRequestCacheThrottlingValidator(60, 3)
        request = self._make_request()
        validator._validate(request)
        validator._validate(request)
        validator._validate(request)
        assert_false(validator._validate(request))

    @override_settings(SECURITY_THROTTLING_ENABLED=True)
    def test_validate_raises_throttling_exception_when_over_limit(self):
        validator = PerRequestCacheThrottlingValidator(60, 2)
        request = self._make_request()
        validator.validate(request)
        validator.validate(request)
        with assert_raises(ThrottlingException):
            validator.validate(request)

    @override_settings(SECURITY_THROTTLING_ENABLED=True)
    def test_different_ips_are_counted_independently(self):
        validator = PerRequestCacheThrottlingValidator(60, 2)
        request_a = self._make_request(ip='10.0.0.1')
        request_b = self._make_request(ip='10.0.0.2')
        validator._validate(request_a)
        validator._validate(request_a)
        # IP A is at limit
        assert_false(validator._validate(request_a))
        # IP B is independent
        assert_true(validator._validate(request_b))

    @override_settings(SECURITY_THROTTLING_ENABLED=True)
    def test_different_paths_are_counted_independently(self):
        validator = PerRequestCacheThrottlingValidator(60, 2)
        request_a = self._make_request(path='/path-a/')
        request_b = self._make_request(path='/path-b/')
        validator._validate(request_a)
        validator._validate(request_a)
        assert_false(validator._validate(request_a))
        assert_true(validator._validate(request_b))

    @override_settings(SECURITY_THROTTLING_ENABLED=False)
    def test_throttling_disabled_always_passes(self):
        validator = PerRequestCacheThrottlingValidator(60, 1)
        request = self._make_request()
        validator.validate(request)
        validator.validate(request)
        validator.validate(request)
