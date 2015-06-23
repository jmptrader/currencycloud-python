import pytest
from betamax import Betamax
from mock import patch
import requests_mock
import re

import currencycloud
from currencycloud.errors import *

class TestError:
    def setup_method(self, method):
        currencycloud.reset_session()
        currencycloud.environment = currencycloud.ENV_DEMOSTRATION
        currencycloud.login_id = 'rjnienaber@gmail.com'
        currencycloud.api_key = 'ef0fd50fca1fb14c1fab3a8436b9ecb65f02f129fd87eafa45ded8ae257528f0'
        currencycloud.token = None

    def test_error_contains_full_details_for_api_error(self):
        currencycloud.login_id = 'non-existent-login-id'
        currencycloud.api_key = 'ef0fd50fca1fb14c1fab3a8436b9ecb57528f0'

        session = currencycloud.session(authenticate=False)
        with Betamax(session.requests_session) as betamax:
            betamax.use_cassette('error/contains_full_details_for_api_error')
            error = None
            try:
                currencycloud.session().authenticate()

                raise Exception("Should have failed")
            except BadRequestError, e:
                error = e

        assert error is not None

        expected_error_fields = [
            "platform: {platform}".format(platform=error.platform),
            "login_id: non-existent-login-id",
            "api_key: " + currencycloud.api_key,
            "verb: post",
            "url: https://devapi.thecurrencycloud.com/v2/authenticate/api",
            "status_code: 400",
            "date:",
            "request_id:",
            "field: api_key",
            "code: api_key_length_is_invalid",
            "message: api_key should be 64 character(s) long",
            "length: 64"
        ]

        error_str = str(error)
        missing = False
        for f in expected_error_fields:
            if f not in error_str:
                missing = True
                break

        assert missing is False

    def test_error_is_raised_on_bad_request(self):
        currencycloud.login_id = 'non-existent-login-id'
        currencycloud.api_key = 'ef0fd50fca1fb14c1fab3a8436b9ecb57528f0'

        session = currencycloud.session(authenticate=False)
        with Betamax(session.requests_session) as betamax:
            betamax.use_cassette('error/is_raised_on_bad_request')
            error = None
            try:
                currencycloud.session().authenticate()

                raise Exception("Should have failed")
            except BadRequestError, e:
                error = e

            assert error.code == 'auth_invalid_user_login_details'
            assert error.raw_response != None
            assert error.status_code == 400
            assert len(error.messages) == 1

            error_message = error.messages[0]
            assert error_message.field == 'api_key'
            assert error_message.code == 'api_key_length_is_invalid'
            assert error_message.message == 'api_key should be 64 character(s) long'
            assert error_message.params["length"] == 64

    def test_error_is_raised_on_incorrect_authentication_details(self):
        currencycloud.login_id = 'non-existent-login-id'
        currencycloud.api_key = 'efb5ae2af84978b7a37f18dd61c8bbe139b403009faea83484405a3dcb64c4d8'

        session = currencycloud.session(authenticate=False)
        with Betamax(session.requests_session) as betamax:
            betamax.use_cassette('error/is_raised_on_incorrect_authentication_details')
            error = None
            try:
                currencycloud.session().authenticate()

                raise Exception("Should have failed")
            except AuthenticationError, e:
                error = e

            assert error.code == 'auth_failed'
            assert error.raw_response != None
            assert error.status_code == 401
            assert len(error.messages) == 1

            error_message = error.messages[0]
            assert error_message.field == 'username'
            assert error_message.code == 'invalid_supplied_credentials'
            assert error_message.message == 'Authentication failed with the supplied credentials'
            assert not error_message.params

    def test_error_is_raised_on_unexpected_error(self):
        error = None

        session = currencycloud.session(authenticate=False)
        with requests_mock.Mocker() as mock:
            def request_tester(request, context):
                raise Exception('Unexpected Error')
            mock.post(re.compile('.*'), json=request_tester)

            with Betamax(session.requests_session) as betamax:
                betamax.use_cassette('error/is_raised_on_unexpected_error')
                try:
                    currencycloud.session().authenticate()

                    raise Exception("Should have failed")
                except UnexpectedError, e:
                    error = e

        assert error is not None

        expected_error_fields = [
            "platform: {platform}".format(platform=error.platform),
            "login_id: rjnienaber@gmail.com",
            "api_key: " + currencycloud.api_key,
            "verb: post",
            "url: https://devapi.thecurrencycloud.com/v2/authenticate/api",
            "inner_error: Exception('Unexpected Error'",
        ]

        error_str = str(error)
        missing = False
        for f in expected_error_fields:
            if f not in error_str:
                missing = True
                break

        assert missing is False
        assert error.inner_error is not None
        assert isinstance(error.inner_error, Exception)

    # def test_error_is_raised_on_a_forbidden_request(self):

    #     session = currencycloud.session(authenticate=False)
    #     with Betamax(session.requests_session) as betamax:
    #         betamax.use_cassette('error/is_raised_on_a_forbidden_request')
    #         error = None
    #         try:
    #             currencycloud.session().authenticate()

    #             raise Exception("Should have failed")
    #         except ForbiddenError, e:
    #             error = e

    #         assert error.code == 'auth_failed'
    #         assert error.raw_response != None
    #         assert error.status_code == 403
    #         assert len(error.messages) == 1

    #         error_message = error.messages[0]
    #         assert error_message.field == 'username'
    #         assert error_message.code == 'invalid_supplied_credentials'
    #         assert error_message.message == 'Authentication failed with the supplied credentials'
    #         assert not error_message.params
