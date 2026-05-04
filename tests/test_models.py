from models import Dataset

def test_dataset_short_desc():
    ds = Dataset(
        title="Test Dataset",
        source="test",
        url="http://example.com",
        description="This is a very long description that should be truncated by the short_desc method because it exceeds the maximum length."
    )
    assert len(ds.short_desc(20)) == 21  # 20 chars + ellipsis
    assert ds.short_desc(20).endswith("…")
    assert ds.short_desc(1000) == "This is a very long description that should be truncated by the short_desc method because it exceeds the maximum length."

def test_dataset_format_tags():
    ds = Dataset(title="T", source="s", url="u", tags=["tag1", "tag2", "tag3"])
    assert ds.format_tags() == "tag1, tag2, tag3"

    ds_empty = Dataset(title="T", source="s", url="u", tags=[])
    assert ds_empty.format_tags() == "-"

def test_dataset_format_formats():
    ds = Dataset(title="T", source="s", url="u", file_formats=["CSV", "JSON"])
    assert ds.format_formats() == "CSV, JSON"

    ds_empty = Dataset(title="T", source="s", url="u", file_formats=[])
    assert ds_empty.format_formats() == "-"
