import pytest
import respx
from httpx import Response
from searchers import kaggle_search, huggingface_search, openml_search
from unittest.mock import patch

@pytest.mark.asyncio
@respx.mock
async def test_kaggle_search():
    respx.get("https://www.kaggle.com/api/v1/datasets/list").mock(return_value=Response(200, json=[
        {
            "ref": "test/dataset",
            "title": "Test Kaggle",
            "subtitle": "A test dataset",
            "tags": [{"name": "test"}],
            "totalBytes": 1024,
            "licenseName": "MIT",
            "downloadCount": 100,
            "voteCount": 10,
            "ownerName": "tester",
            "lastUpdated": "2023-01-01T00:00:00Z"
        }
    ]))

    with patch("searchers.kaggle_search.KAGGLE_USERNAME", "fake"), \
         patch("searchers.kaggle_search.KAGGLE_KEY", "fake"):
        results = await kaggle_search.search("test")
        assert len(results) == 1
        assert results[0].title == "Test Kaggle"
        assert results[0].source == "kaggle"
        assert results[0].size == "1.0 KB"

@pytest.mark.asyncio
@respx.mock
async def test_huggingface_search():
    respx.get("https://huggingface.co/api/datasets").mock(return_value=Response(200, json=[
        {
            "id": "test/hf-dataset",
            "cardData": {"description": "HF test description"},
            "tags": ["nlp", "text"],
            "downloads": 500,
            "likes": 50,
            "author": "hftester",
            "lastModified": "2023-02-01T00:00:00Z"
        }
    ]))

    results = await huggingface_search.search("test")
    assert len(results) == 1
    assert results[0].title == "test/hf-dataset"
    assert results[0].source == "huggingface"
    assert results[0].description == "HF test description"

@pytest.mark.asyncio
@respx.mock
async def test_openml_search():
    respx.get("https://www.openml.org/api/v1/json/data/list/search/test").mock(return_value=Response(200, json={
        "data": {
            "dataset": [
                {
                    "did": "1",
                    "name": "OpenML Test",
                    "status": "active",
                    "format": "ARFF",
                    "creator": "omltester",
                    "last_output": "2023-03-01"
                }
            ]
        }
    }))

    results = await openml_search.search("test")
    assert len(results) == 1
    assert results[0].title == "OpenML Test"
    assert results[0].source == "openml"
    assert results[0].file_formats == ["ARFF"]

@pytest.mark.asyncio
@respx.mock
async def test_openml_search_no_results():
    respx.get("https://www.openml.org/api/v1/json/data/list/search/empty").mock(return_value=Response(404))
    results = await openml_search.search("empty")
    assert results == []
