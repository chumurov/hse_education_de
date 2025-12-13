import pytest
try:
    from shorturl_app.models import URLItem, URLCreate
except ImportError:
    URLItem = None
    URLCreate = None

def test_url_create_model():
    if URLCreate is None:
        pytest.fail("URLCreate model not implemented")
    url = URLCreate(url="https://example.com")
    assert str(url.url) == "https://example.com/"

def test_url_item_model():
    if URLItem is None:
        pytest.fail("URLItem model not implemented")
    url = URLItem(id="abc12345", url="https://example.com")
    assert url.id == "abc12345"
    assert str(url.url) == "https://example.com/"
