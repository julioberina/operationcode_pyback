#!flask/bin/python
import json
import logging

import pytest
import config.configs
import ocbot.web.routes
from tests.handler_tests.action_menu_events import SUGGESTION_CLICKED_EVENT
from tests.test_data import CHALLENGE, NEW_MEMBER
from pytest_mock import mocker

logging.disable(logging.CRITICAL)

GOOD_TOKEN = 'token'


@pytest.fixture
def test_app():
    config.configs.configs['VERIFICATION_TOKEN'] = GOOD_TOKEN
    from ocbot import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['DEBUG'] = False
    return app.test_client()


# Request Verification Tests #
def test_good_slack_token(mocker: mocker, test_app):
    data = NEW_MEMBER
    data['token'] = GOOD_TOKEN
    json_data = json.dumps(data)
    mock = mocker.patch('ocbot.web.routes.RoutingHandler')
    response = test_app.post('/event_endpoint', data=json_data,
                             content_type='application/json',
                             follow_redirects=True)
    assert mock.called
    assert response.status_code == 200


def test_event_with_bad_slack_token(mocker, test_app):
    data = NEW_MEMBER
    data['token'] = 'bad token'
    json_data = json.dumps(data)
    mocker.patch('ocbot.web.routes.RoutingHandler')
    response = test_app.post('/event_endpoint', data=json_data,
                             content_type='application/json',
                             follow_redirects=True)
    assert not ocbot.web.routes.RoutingHandler.called
    assert response.status_code == 403


def test_interaction_with_bad_slack_token(mocker, test_app):
    data = SUGGESTION_CLICKED_EVENT
    data['token'] = 'bad token'
    json_data = json.dumps(data)
    mocker.patch('ocbot.web.routes.RoutingHandler')
    response = test_app.post('/user_interaction', data=dict(payload=json_data),
                             follow_redirects=True)
    assert not ocbot.web.routes.RoutingHandler.called
    assert response.status_code == 403


def test_empty_slack_value_token(mocker, test_app):
    data = NEW_MEMBER
    data['token'] = None
    json_data = json.dumps(data)
    mocker.patch('ocbot.web.routes.RoutingHandler')
    response = test_app.post('/event_endpoint', data=json_data,
                             content_type='application/json',
                             follow_redirects=True)
    assert not ocbot.web.routes.RoutingHandler.called
    assert response.status_code == 403


def test_empty_token_slack_data(mocker, test_app):
    mocker.patch('ocbot.web.routes.RoutingHandler')
    response = test_app.post('/event_endpoint', data=None,
                             content_type='application/json',
                             follow_redirects=True)
    assert not ocbot.web.routes.RoutingHandler.called
    assert response.status_code == 400


# Challenge verification tests #
def test_challenge_redirect(mocker, test_app):
    data = json.dumps(CHALLENGE)
    mocker.patch('ocbot.web.routes.RoutingHandler')
    response = test_app.post('/event_endpoint', data=data,
                             content_type='application/json',
                             follow_redirects=True)
    assert not ocbot.web.routes.RoutingHandler.called
    assert response.status_code == 200


def test_url_verified_called(mocker, test_app):
    """
    :param mock: combined_route_director, don't want to call function
    :return:
    This case tests if we have a verification token
    """
    CHALLENGE['token'] = GOOD_TOKEN
    data = json.dumps(CHALLENGE)
    mocker.patch('ocbot.web.routes.RoutingHandler')
    mocker.patch('ocbot.web.routes.validate_response')

    response = test_app.post('/event_endpoint', data=data,
                             content_type='application/json',
                             follow_redirects=True)

    assert not ocbot.web.routes.RoutingHandler.called
    assert not ocbot.web.routes.validate_response.called
    assert response.status_code == 200
