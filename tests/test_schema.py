from src.shared.schema import make_clean_record, validate_clean_record


def test_make_and_validate_clean_record():
    text = "This is a reasonably long piece of text about machine learning and statistics. " * 2

    rec = make_clean_record(
        source="academic",
        subsource="sample",
        raw_id="123",
        text=text,
        lang_hint="en",
    )

    assert validate_clean_record(rec), "Clean record did not pass validation"

    assert rec["id"] == "academic_123"
    assert rec["source"] == "academic"
    assert rec["subsource"] == "sample"
    assert rec["lang"] == "en"
    assert isinstance(rec["length_tokens"], int)
    assert rec["length_tokens"] > 10
    assert isinstance(rec["quality_score"], float)
    assert isinstance(rec["text"], str)
    assert rec["text"].strip() != ""
