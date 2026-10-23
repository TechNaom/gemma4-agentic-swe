# Escaped mutants: manual review

For each planted bug that the tests did NOT catch, decide:

- **W** (weak test): the change really breaks behaviour, and the tests miss it
- **E** (equivalent): the change does not alter behaviour (e.g. `return False` -> `return None` used only as a boolean)
- **?** unsure

| Task | Operator | File | Before | After | Verdict (W/E/?) |
|---|---|---|---|---|---|
| fastapi_11194 | drop_line | `fastapi/dependencies/utils.py` | `and isinstance(field_info, params.File)` | `<deleted>` | |
| fastapi_14306 | bool_swap | `fastapi/exceptions.py` | `class EndpointContext(TypedDict, total=False):` | `class EndpointContext(TypedDict, total=T` | |
| fastapi_14372 | drop_line | `fastapi/dependencies/utils.py` | `depends = dataclasses.replace(depends, dependency=type_annot` | `<deleted>` | |
| fastapi_14419 | drop_line | `fastapi/dependencies/utils.py` | `own_oauth_scopes: List[str] = []` | `<deleted>` | |
| fastapi_14458 | return_none | `fastapi/dependencies/models.py` | `return False` | `return None` | |
| fastapi_14616 | drop_line | `fastapi/dependencies/utils.py` | `and isinstance(values, (ImmutableMultiDict, Headers))` | `<deleted>` | |
| fastapi_15280 | drop_file | `docs_src/vibe/tutorial001_py310.py` | `2 files` | `1 files` | |
| fastapi_15280 | drop_line | `docs_src/vibe/tutorial001_py310.py` | `app = FastAPI()` | `<deleted>` | |
| fastapi_15661 | bool_swap | `scripts/prepare_release.py` | `exists=True,` | `exists=False,` | |
| fastapi_15661 | drop_line | `scripts/prepare_release.py` | `file_okay=True,` | `<deleted>` | |
| fastapi_15661 | off_by_one | `scripts/prepare_release.py` | `1,` | `2,` | |
| fastapi_15800 | bool_swap | `fastapi/routing.py` | `] = True,` | `] = False,` | |
| rich_3052 | bool_swap | `rich/prompt.py` | `case_sensitive: bool = True,` | `case_sensitive: bool = False,` | |
| rich_3052 | drop_line | `rich/prompt.py` | `case_sensitive=False,` | `<deleted>` | |
| rich_3061 | flip_compare | `rich/text.py` | `tab_size: int = console.tab_size if self.tab_size is None el` | `tab_size: int = console.tab_size if self` | |
| rich_3061 | return_none | `rich/text.py` | `return self` | `return None` | |
| rich_3180 | bool_swap | `rich/_wrap.py` | `def divide_line(text: str, width: int, fold: bool = True) ->` | `def divide_line(text: str, width: int, f` | |
| rich_3180 | off_by_one | `rich/_wrap.py` | `cell_offset = 0` | `cell_offset = 1` | |
| rich_3468 | bool_swap | `rich/console.py` | `self.quiet = True` | `self.quiet = False` | |
| rich_3506 | off_by_one | `rich/segment.py` | `pos = int((cut / cell_length) * (len(text))) - 1` | `pos = int((cut / cell_length) * (len(tex` | |
| rich_3535 | drop_file | `rich/segment.py` | `2 files` | `1 files` | |
| rich_3535 | drop_line | `rich/segment.py` | `cut (int): Offset within the segment to cut.` | `<deleted>` | |
| rich_3675 | drop_file | `rich/diagnose.py` | `2 files` | `1 files` | |
| rich_3676 | bool_swap | `rich/default_styles.py` | `"traceback.note": Style(color="green", bold=True),` | `"traceback.note": Style(color="green", b` | |
| rich_3676 | drop_line | `rich/traceback.py` | `notes=notes,` | `<deleted>` | |
| rich_3772 | bool_swap | `rich/traceback.py` | `exc_value, "__suppress_context__", False` | `exc_value, "__suppress_context__", True` | |
| rich_3772 | drop_line | `rich/traceback.py` | `exc_type = cause.__class__` | `<deleted>` | |
| rich_3777 | bool_swap | `rich/console.py` | `force_interactive = False` | `force_interactive = True` | |
| rich_3777 | drop_file | `rich/diagnose.py` | `2 files` | `1 files` | |
| rich_3894 | drop_line | `rich/_inspect.py` | `qualname = getattr(obj, "__name__", name)` | `<deleted>` | |
| rich_3930 | drop_line | `rich/_unicode_data/unicode12-1-0.py` | `"◻",` | `<deleted>` | |
| rich_3930 | off_by_one | `rich/_unicode_data/unicode17-0-0.py` | `(3636, 3642, 0),` | `(3637, 3642, 0),` | |
| rich_3934 | off_by_one | `rich/live_render.py` | `return 0` | `return 1` | |
| rich_3935 | flip_compare | `rich/table.py` | `if column_index == 0:` | `if column_index != 0:` | |
| rich_4075 | bool_swap | `rich/console.py` | `styles: bool = False,` | `styles: bool = True,` | |
