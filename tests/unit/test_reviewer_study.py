"""Exercise the registered scorer's closed response contract."""

from copy import deepcopy

from p3if.reviewer_study import _Response, _score_row


def test_score_requires_complete_exact_change():
    answer = {
        "case_id": "R01",
        "classification": "declared_change",
        "events": [
            {
                "id": "link",
                "change": "modified",
                "fields": ["process_id", "strength"],
                "before": {
                    "endpoints": ["property", "old", "perspective"],
                    "scores": {"strength": "reported_zero", "confidence": "omitted"},
                },
                "after": {
                    "endpoints": ["property", "new", "perspective"],
                    "scores": {"strength": "explicit_null", "confidence": "omitted"},
                },
            },
        ],
    }
    expected = _Response.model_validate(answer)
    received = deepcopy(answer)
    received["events"][0]["fields"].reverse()
    assert _score_row(expected, received) == "correct"
    received["events"][0]["after"]["scores"]["strength"] = "omitted"
    assert _score_row(expected, received) == "incorrect"
    assert _score_row(expected, {"case_id": "R01"}) == "malformed"
    assert _score_row(expected, None) == "missing"
