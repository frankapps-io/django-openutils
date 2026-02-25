import pytest

from tests.models import TrackedModel


@pytest.mark.django_db
class TestModelDiffMixin:
    """Tests for ModelDiffMixin using TrackedModel as the concrete model."""

    def test_no_unsaved_changes_after_create(self):
        obj = TrackedModel.objects.create(name="hello")
        assert not obj.has_unsaved_changes

    def test_detects_unsaved_change(self):
        obj = TrackedModel.objects.create(name="hello")
        obj.name = "world"
        assert obj.has_unsaved_changes
        assert "name" in obj.unsaved_fields

    def test_no_unsaved_changes_after_save(self):
        obj = TrackedModel.objects.create(name="hello")
        obj.name = "world"
        obj.save()
        assert not obj.has_unsaved_changes

    def test_recent_updates_after_save(self):
        obj = TrackedModel.objects.create(name="hello")
        obj.name = "world"
        obj.save()
        assert obj.has_updated_fields
        assert "name" in obj.updated_fields
        old, new = obj.recent_updates["name"]
        assert old == "hello"
        assert new == "world"

    def test_only_auto_fields_in_recent_updates_when_nothing_changed(self):
        obj = TrackedModel.objects.create(name="hello")
        # Save again without changing anything — only auto_now fields should differ
        obj.save()
        assert set(obj.updated_fields) == {"modified_at"}

    def test_reset_after_refresh_from_db(self):
        obj = TrackedModel.objects.create(name="hello")
        obj.name = "world"
        assert obj.has_unsaved_changes

        obj.refresh_from_db()
        assert not obj.has_unsaved_changes
        assert obj.name == "hello"  # back to DB value

    def test_get_or_create_existing_has_no_changes(self):
        TrackedModel.objects.create(name="hello")
        obj, created = TrackedModel.objects.get_or_create(name="hello")
        assert not created
        assert not obj.has_unsaved_changes

    def test_setting_same_value_is_not_a_change(self):
        obj = TrackedModel.objects.create(name="hello")
        obj.name = "hello"
        assert not obj.has_unsaved_changes

    def test_tracks_json_field_changes(self):
        obj = TrackedModel.objects.create(name="hello", tags=[])
        obj.tags = ["a", "b"]
        assert obj.has_unsaved_changes
        assert "tags" in obj.unsaved_fields

    def test_unsaved_field_diff(self):
        obj = TrackedModel.objects.create(name="hello")
        obj.name = "world"
        diff = obj.get_unsaved_field_diff("name")
        assert diff == ("hello", "world")

    def test_unsaved_field_diff_returns_none_for_unchanged(self):
        obj = TrackedModel.objects.create(name="hello")
        assert obj.get_unsaved_field_diff("name") is None

    def test_deferred_fields_not_tracked(self):
        """Deferred fields aren't in __dict__ so shouldn't appear in diffs."""
        TrackedModel.objects.create(name="hello")
        obj = TrackedModel.objects.defer("name").get(name="hello")
        # name is deferred — not in snapshot
        assert "name" not in obj.unsaved_changes
