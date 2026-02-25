from copy import copy


class ModelDiffMixin:
    """
    A Django model mixin that tracks field changes via ``__dict__`` snapshotting.

    Uses concrete field attnames (e.g. ``venue_id`` not ``venue``) so FK fields
    are compared by PK value — no extra DB queries. Deferred fields are simply
    excluded from tracking (they aren't in ``__dict__`` until accessed).

    Hooks into ``__init__``, ``save``, and ``refresh_from_db`` to keep snapshots
    in sync.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reset_diff(save_previous=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._reset_diff(save_previous=True)

    def refresh_from_db(self, *args, **kwargs):
        super().refresh_from_db(*args, **kwargs)
        self._reset_diff(save_previous=False)

    # -- internal helpers --

    def _snapshot(self) -> dict:
        attnames = {f.attname for f in self._meta.concrete_fields}
        return {k: copy(v) for k, v in self.__dict__.items() if k in attnames}

    def _reset_diff(self, *, save_previous: bool) -> None:
        if save_previous:
            self.__previous = getattr(self, "_ModelDiffMixin__initial", None)
        else:
            self.__previous = None
        self.__initial = self._snapshot()

    @staticmethod
    def _get_diffs(d1: dict, d2: dict) -> dict:
        return {k: (v, d2[k]) for k, v in d1.items() if k in d2 and v != d2[k]}

    # -- unsaved changes (current in-memory state vs last save/load) --

    @property
    def unsaved_changes(self) -> dict:
        return self._get_diffs(self.__initial, self._snapshot())

    @property
    def has_unsaved_changes(self) -> bool:
        return bool(self.unsaved_changes)

    @property
    def unsaved_fields(self):
        return self.unsaved_changes.keys()

    def get_unsaved_field_diff(self, field_name: str) -> tuple | None:
        return self.unsaved_changes.get(field_name)

    # -- recent updates (changes from the last save() call) --

    @property
    def recent_updates(self) -> dict:
        if self.__previous is None:
            return {}
        return self._get_diffs(self.__previous, self.__initial)

    @property
    def has_updated_fields(self) -> bool:
        return bool(self.recent_updates)

    @property
    def updated_fields(self):
        return self.recent_updates.keys()
