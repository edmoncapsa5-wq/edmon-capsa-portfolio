"""Synthetic SME FAQ intake. Portfolio demo; never sends real messages."""
import hmac
import os
import re
import sqlite3
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

FAQ = {
    'hours': (r'\bhours\b', r'\bopen\b', r'\bclosing\b'),
    'pricing': (r'\bprice\b', r'\bpricing\b', r'\bcost\b', r'\brate\b'),
    'booking': (r'\bbook\b', r'\bbooking\b', r'\bappointment\b', r'\bschedule\b'),
}
ANSWERS = {
    'hours': 'DEMO: Support hours are Monday to Friday, 9 AM–5 PM.',
    'pricing': 'DEMO: Please request the approved service rate card.',
    'booking': 'DEMO: Share a preferred day; a person will confirm availability.',
}
STOP_WORDS = {'stop', 'unsubscribe', 'opt out', 'cancel messages'}

class Inbound(BaseModel):
    message_id: str = Field(min_length=1, max_length=128)
    customer_id: str = Field(min_length=1, max_length=128)
    text: str = Field(min_length=1, max_length=2000)

class Decision(BaseModel):
    message_id: str
    status: Literal['draft_pending_approval', 'handoff', 'opted_out', 'suppressed', 'approved']
    faq_topic: str | None = None
    draft_reply: str | None = None
    reason: str

class Approval(BaseModel):
    approved: bool


def match_topic(message: str) -> str | None:
    norm = ' '.join(re.findall(r'[a-z]+', message.casefold()))
    if norm in STOP_WORDS:
        return '__opt_out__'
    scores = [(sum(bool(re.search(pattern, norm)) for pattern in patterns), topic)
              for topic, patterns in FAQ.items()]
    scores = sorted((score, topic) for score, topic in scores if score > 0)[::-1]
    if not scores or (len(scores) > 1 and scores[0][0] == scores[1][0]):
        return None
    return scores[0][1]


def create_app(db_path: str, webhook_secret: str, admin_token: str) -> FastAPI:
    if not webhook_secret or not admin_token:
        raise ValueError('Explicit webhook and admin keys required')
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    def connect():
        con = sqlite3.connect(db_path, timeout=10)
        con.row_factory = sqlite3.Row
        return con
    with connect() as con:
        con.execute('CREATE TABLE IF NOT EXISTS inbound (message_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, status TEXT NOT NULL, faq_topic TEXT, draft_reply TEXT, reason TEXT NOT NULL)')
        con.execute('CREATE TABLE IF NOT EXISTS optouts (customer_id TEXT PRIMARY KEY)')
    api = FastAPI(title='Synthetic Human-Reviewed FAQ Intake', version='1.0')

    def require(provided, expected):
        if provided is None or not hmac.compare_digest(provided, expected):
            raise HTTPException(401, 'Not authorized')

    @api.post('/webhook/mock', response_model=Decision)
    def inbound(payload: Inbound, x_demo_webhook_key: str | None = Header(default=None)):
        require(x_demo_webhook_key, webhook_secret)
        with connect() as con:
            prior = con.execute('SELECT * FROM inbound WHERE message_id=?', (payload.message_id,)).fetchone()
            if prior:
                return Decision(message_id=prior['message_id'], status=prior['status'], faq_topic=prior['faq_topic'], draft_reply=prior['draft_reply'], reason=prior['reason'])
            opted_out = con.execute('SELECT 1 FROM optouts WHERE customer_id=?', (payload.customer_id,)).fetchone()
            topic = match_topic(payload.text)
            if topic == '__opt_out__':
                con.execute('INSERT OR IGNORE INTO optouts VALUES (?)', (payload.customer_id,))
                status, topic, reply, reason = 'opted_out', None, None, 'Opt-out recorded; no external sending'
            elif opted_out:
                status, topic, reply, reason = 'suppressed', None, None, 'Previous opt-out blocks response'
            elif topic is None:
                status, reply, reason = 'handoff', None, 'Unknown or ambiguous; human response required'
            else:
                status, reply, reason = 'draft_pending_approval', ANSWERS[topic], 'Draft only; human approval required'
            con.execute('INSERT INTO inbound VALUES (?, ?, ?, ?, ?, ?)', (payload.message_id, payload.customer_id, status, topic, reply, reason))
            return Decision(message_id=payload.message_id, status=status, faq_topic=topic, draft_reply=reply, reason=reason)

    @api.post('/review/{message_id}', response_model=Decision)
    def review(message_id: str, vote: Approval, x_demo_admin_token: str | None = Header(default=None)):
        require(x_demo_admin_token, admin_token)
        with connect() as con:
            row = con.execute('SELECT * FROM inbound WHERE message_id=?', (message_id,)).fetchone()
            if not row:
                raise HTTPException(404, 'Unknown message')
            if row['status'] != 'draft_pending_approval':
                raise HTTPException(409, 'Not awaiting approval')
            opted_out = con.execute('SELECT 1 FROM optouts WHERE customer_id=?', (row['customer_id'],)).fetchone()
            if opted_out:
                status, reason = 'suppressed', 'Customer opted out before approval'
            elif vote.approved:
                status, reason = 'approved', 'Approval recorded, but external sending is disabled'
            else:
                status, reason = 'handoff', 'Draft rejected; human response required'
            con.execute('UPDATE inbound SET status=?, reason=? WHERE message_id=?', (status, reason, message_id))
            return Decision(message_id=message_id, status=status, faq_topic=row['faq_topic'], draft_reply=row['draft_reply'] if status == 'approved' else None, reason=reason)

    @api.get('/health')
    def health():
        return {'ok': True, 'mode': 'synthetic-only', 'external_sends': False}
    return api

# Localhost-only demo defaults. Do not run on a public interface.
app = create_app(os.environ.get('DEMO_DB_PATH', '/tmp/sme_faq_demo.sqlite'),
                 os.environ.get('WEBHOOK_SECRET', 'demo-local-webhook-only'),
                 os.environ.get('ADMIN_TOKEN', 'demo-local-admin-only'))
