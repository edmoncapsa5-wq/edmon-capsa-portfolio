from fastapi.testclient import TestClient
from app import create_app, match_topic
import pytest

@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(str(tmp_path / 'test.sqlite'), 'secret-in', 'secret-admin'))

def send(client, id, text, customer='C1', key='secret-in'):
    return client.post('/webhook/mock', json={'message_id': id, 'customer_id': customer, 'text': text}, headers={'X-Demo-Webhook-Key': key})

def review(client, id, approved=True, key='secret-admin'):
    return client.post('/review/' + id, json={'approved': approved}, headers={'X-Demo-Admin-Token': key})

def test_known_question_creates_draft_not_external_send(client):
    r = send(client, 'm1', 'What are your opening hours?')
    assert r.status_code == 200
    assert r.json()['status'] == 'draft_pending_approval'
    assert r.json()['faq_topic'] == 'hours'
    assert client.get('/health').json()['external_sends'] is False

def test_unknown_question_requires_human(client):
    assert send(client, 'm2', 'Can you recommend something custom?').json()['status'] == 'handoff'

def test_ambiguous_question_requires_human(client):
    assert send(client, 'm3', 'Can I book and get a price?').json()['status'] == 'handoff'

def test_duplicate_message_is_idempotent(client):
    first = send(client, 'm4', 'pricing')
    second = send(client, 'm4', 'completely different words')
    assert first.json() == second.json()

def test_optout_blocks_new_and_queued_replies(client):
    assert send(client, 'm5', 'cost', 'C2').json()['status'] == 'draft_pending_approval'
    assert send(client, 'm6', 'STOP', 'C2').json()['status'] == 'opted_out'
    assert send(client, 'm7', 'hours', 'C2').json()['status'] == 'suppressed'
    assert review(client, 'm5').json()['status'] == 'suppressed'

def test_review_authorization_and_transitions(client):
    send(client, 'm8', 'booking')
    assert review(client, 'm8', key='wrong').status_code == 401
    assert review(client, 'm8').json()['status'] == 'approved'
    assert review(client, 'm8').status_code == 409

def test_bad_webhook_key_rejected(client):
    assert send(client, 'm9', 'pricing', key='wrong').status_code == 401

def test_rejected_draft_escalates(client):
    send(client, 'm10', 'What does it cost?')
    assert review(client, 'm10', approved=False).json()['status'] == 'handoff'

def test_matcher():
    assert match_topic('OPENING HOURS!') == 'hours'
    assert match_topic('STOP') == '__opt_out__'
    assert match_topic('something unrecognized') is None
