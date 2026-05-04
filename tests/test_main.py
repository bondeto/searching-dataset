import pytest
from unittest.mock import AsyncMock, patch
from main import perform_search
from models import Dataset

@pytest.mark.asyncio
async def test_perform_search_aggregates_results():
    mock_kaggle_res = [Dataset(title="Kaggle Result", source="kaggle", url="k")]
    mock_hf_res = [Dataset(title="HF Result", source="huggingface", url="h")]

    with patch("searchers.kaggle_search.search", new_callable=AsyncMock) as mock_kaggle, \
         patch("searchers.huggingface_search.search", new_callable=AsyncMock) as mock_hf, \
         patch("searchers.openml_search.search", new_callable=AsyncMock) as mock_openml:

        mock_kaggle.return_value = mock_kaggle_res
        mock_hf.return_value = mock_hf_res
        mock_openml.return_value = []

        results = await perform_search("test", limit=10)

        assert len(results) == 2
        sources = [r.source for r in results]
        assert "kaggle" in sources
        assert "huggingface" in sources

@pytest.mark.asyncio
async def test_perform_search_handles_exceptions():
    with patch("searchers.kaggle_search.search", new_callable=AsyncMock) as mock_kaggle, \
         patch("searchers.huggingface_search.search", new_callable=AsyncMock) as mock_hf, \
         patch("searchers.openml_search.search", new_callable=AsyncMock) as mock_openml:

        mock_kaggle.side_effect = Exception("Kaggle error")
        mock_hf.return_value = [Dataset(title="HF", source="huggingface", url="h")]
        mock_openml.return_value = []

        results = await perform_search("test", limit=10)

        assert len(results) == 1
        assert results[0].source == "huggingface"
