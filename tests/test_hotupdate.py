
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hotupdate.manager import HotUpdateManager


def test_min_version_check():
    hm = HotUpdateManager("1.0.0")
    patch = {"version": "2.0.0", "min_version": "1.5.0"}
    assert hm.apply_patch(patch) == False


def test_version_above_min_passes():
    hm = HotUpdateManager("1.6.0")
    patch = {"version": "2.0.0", "min_version": "1.5.0"}
    assert hm.apply_patch(patch) == True


def test_file_verify_before_apply():
    hm = HotUpdateManager("1.0.0")
    hm.resources["file.txt"] = "old"
    result = hm.verify_and_apply("file.txt", "new", "wrong_hash")
    assert result == False
    assert hm.resources["file.txt"] == "old"


def test_rollback_after_failed_patch():
    hm = HotUpdateManager("1.0.0")
    hm.resources["a.txt"] = "original"
    hm.backup = {"a.txt": "original"}
    hm.apply_patch({"version": "2.0.0", "min_version": "1.0.0", "files": {"a.txt": "new"}})
    hm.rollback()
    assert hm.resources["a.txt"] == "original"


def test_missing_dependency_skipped():
    hm = HotUpdateManager("1.0.0")
    resource = {"name": "new_shader", "dependencies": ["nonexistent_shader"]}
    assert hm.check_dependencies(resource) == False


def test_occupied_resource_deferred():
    hm = HotUpdateManager("1.0.0")
    hm.occupied_resources.add("player_model")
    assert hm.replace_resource("player_model", "new_data") == False
    assert hm.pending_replacements.get("player_model") == "new_data"


def test_db_downgrade_migration():
    hm = HotUpdateManager("2.0.0")
    hm.db_migrations["downgrade_2.0.0_to_1.0.0"] = lambda db: db.pop("new_field", None)
    db = {"old_field": 1, "new_field": 2}
    result = hm.db_downgrade("2.0.0", "1.0.0", db)
    assert "new_field" not in result


def test_grayscale_proportion():
    hm = HotUpdateManager("1.0.0")
    hm.grayscale_config = {"percentage": 10}
    pushed = hm.push_grayscale("patch1", range(100))
    assert len(pushed) <= 10


def test_grayscale_pause():
    hm = HotUpdateManager("1.0.0")
    hm.grayscale_active = True
    hm.pause_grayscale()
    assert hm.grayscale_active == False


def test_backup_created_before_patch():
    hm = HotUpdateManager("1.0.0")
    hm.resources = {"a.txt": "data"}
    hm.apply_patch({"version": "2.0.0", "min_version": "1.0.0", "files": {}})
    assert hm.backup is not None
