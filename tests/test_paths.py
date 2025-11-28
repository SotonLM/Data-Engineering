from pathlib import Path


def test_data_directories_exist():
    """
    Ensure that the expected data directory structure exists.
    This prevents contributors from accidentally deleting or renaming key folders.
    """
    base = Path("data")

    stages = ["raw", "intermediate", "clean", "shard"]
    domains = ["academic", "web", "social", "other"]

    for stage in stages:
        for domain in domains:
            path = base / stage / domain
            assert path.exists(), f"Missing directory: {path}"
