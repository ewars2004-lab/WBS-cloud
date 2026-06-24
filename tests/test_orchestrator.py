from wbs_engine.orchestrator import execute_run


def test_run_mini_fixture_dry_run():
    result = execute_run(dry_run=True, fixture="run_mini.json")
    assert result["audit_passed"]
    assert result["dry_run"]
    assert "run_id" in result
