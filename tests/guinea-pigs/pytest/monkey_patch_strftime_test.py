import time

import pytest


@pytest.fixture()
def patch_time_strftime(monkeypatch):
    monkeypatch.setattr(time, 'strftime', lambda x, y: "spam")


def test_monkeypatch(patch_time_strftime):
    pass
