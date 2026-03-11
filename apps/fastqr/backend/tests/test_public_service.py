import uuid
from types import SimpleNamespace

from app.services import public_service


_ALLOW_ALL_FEATURES = lambda _db, _restaurant_id: {
    "allow_menu": True,
    "allow_votes": True,
    "allow_feedback": True,
    "allow_games": True,
}


class FakeDb:
    def __init__(self):
        self.added = []
        self.committed = False

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True


def test_create_feedback_trims_comment_and_session(monkeypatch):
    fake_db = FakeDb()
    table = SimpleNamespace(id=uuid.uuid4())
    restaurant = SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr(public_service, "get_table_and_restaurant_by_qr", lambda _db, _qr_token: (table, restaurant))
    monkeypatch.setattr(public_service, "_get_restaurant_feature_settings", _ALLOW_ALL_FEATURES)

    result = public_service.create_feedback(fake_db, "token123", 5, "  Great food  ", "  session-a  ")

    assert result == {"status": "received", "rating": 5}
    assert fake_db.committed is True
    assert len(fake_db.added) == 1
    saved_feedback = fake_db.added[0]
    assert saved_feedback.comment == "Great food"
    assert saved_feedback.session_token == "session-a"


def test_create_feedback_converts_blank_comment_to_none(monkeypatch):
    fake_db = FakeDb()
    table = SimpleNamespace(id=uuid.uuid4())
    restaurant = SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr(public_service, "get_table_and_restaurant_by_qr", lambda _db, _qr_token: (table, restaurant))
    monkeypatch.setattr(public_service, "_get_restaurant_feature_settings", _ALLOW_ALL_FEATURES)

    result = public_service.create_feedback(fake_db, "token123", 4, "   ", "session-a")

    assert result == {"status": "received", "rating": 4}
    saved_feedback = fake_db.added[0]
    assert saved_feedback.comment is None


def test_create_feedback_rejects_blank_session_token(monkeypatch):
    fake_db = FakeDb()
    table = SimpleNamespace(id=uuid.uuid4())
    restaurant = SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr(public_service, "get_table_and_restaurant_by_qr", lambda _db, _qr_token: (table, restaurant))
    monkeypatch.setattr(public_service, "_get_restaurant_feature_settings", _ALLOW_ALL_FEATURES)

    try:
        public_service.create_feedback(fake_db, "token123", 5, "ok", "   ")
        assert False, "Expected ValueError for blank session_token"
    except ValueError as exc:
        assert str(exc) == "Invalid session_token"

    assert fake_db.committed is False
    assert fake_db.added == []
