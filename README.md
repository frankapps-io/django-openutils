# django-openutils

Practical Django model utilities. Currently ships **`ModelDiffMixin`** for tracking field changes.

## Installation

```bash
pip install django-openutils
```

## ModelDiffMixin

A model mixin that tracks field changes via `__dict__` snapshotting. Uses concrete field attnames (e.g. `author_id` not `author`) so FK fields are compared by PK value without extra DB queries. Deferred fields are excluded from tracking.

### Usage

```python
from django.db import models
from django_openutils.mixins import ModelDiffMixin


class MyModel(ModelDiffMixin, models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
```

```python
obj = MyModel.objects.create(name="Alice", email="alice@example.com")
obj.has_unsaved_changes  # False

obj.name = "Bob"
obj.has_unsaved_changes  # True
obj.unsaved_fields       # dict_keys(['name'])
obj.get_unsaved_field_diff("name")  # ('Alice', 'Bob')

obj.save()
obj.has_unsaved_changes  # False
obj.has_updated_fields   # True
obj.recent_updates       # {'name': ('Alice', 'Bob')}
```

### API

| Property / Method | Description |
|---|---|
| `unsaved_changes` | Dict of `{field: (old, new)}` for in-memory changes not yet saved |
| `has_unsaved_changes` | `True` if any fields differ from the last save/load |
| `unsaved_fields` | Keys of `unsaved_changes` |
| `get_unsaved_field_diff(field)` | Returns `(old, new)` tuple or `None` |
| `recent_updates` | Dict of `{field: (old, new)}` from the last `save()` call |
| `has_updated_fields` | `True` if `recent_updates` is non-empty |
| `updated_fields` | Keys of `recent_updates` |

## License

MIT - see [LICENSE](LICENSE) for details.
