# Escaped mutants: review

35 of 163 planted bugs passed the tests. For each, is it a real bug the tests missed, or no real change?

- **W** (weak test): the change really breaks behaviour, and the tests miss it
- **E** (equivalent mutant): the change does not alter behaviour
- **?** depends on inputs or callers outside the tested code

**Suggested** verdicts were pre-filled from reading each change in context of the reference patch
(2026-10-24). The owner confirms or overrules in **Your verdict**; the final count uses Your verdict where filled.

Suggested totals: **W 24**, **E 8**, **? 3**. If all suggestions hold, the tests miss a real bug in
**24/163 = 14.7%** of planted bugs (upper bound 16.6% counting ?), down from the raw 35/163 = 21.5%.

| Task | Operator | File | Before | After | Suggested | Why | Your verdict |
|---|---|---|---|---|---|---|---|
| fastapi_11194 | drop_line | `fastapi/dependencies/utils.py` | `and isinstance(field_info, params.File)` | `<deleted>` | **W** | Drops a condition: sequences of non-File bytes fields would now be read as uploads. | **W** |
| fastapi_14306 | bool_swap | `fastapi/exceptions.py` | `class EndpointContext(TypedDict, total=False):` | `class EndpointContext(TypedDict, total=True):` | **E** | `total=` only matters to static type checkers; no runtime effect. (Owner agreed.) | **E** |
| fastapi_14372 | drop_line | `fastapi/dependencies/utils.py` | `depends = dataclasses.replace(depends, dependency=type_` | `<deleted>` | **W** | `depends.dependency` is never set, so `Depends()` with a type annotation loses its dependency. | **W** |
| fastapi_14419 | drop_line | `fastapi/dependencies/utils.py` | `own_oauth_scopes: List[str] = []` | `<deleted>` | **W** | `own_oauth_scopes` is used on the next line but never defined: NameError whenever this path runs. | **W** |
| fastapi_14458 | return_none | `fastapi/dependencies/models.py` | `return False` | `return None` | **E** | `None` and `False` behave the same where `is_gen_callable` is used (truthiness). | **E** |
| fastapi_14616 | drop_line | `fastapi/dependencies/utils.py` | `and isinstance(values, (ImmutableMultiDict, Headers))` | `<deleted>` | **W** | Removes the multi-dict check: `.getlist` is called on plain dicts and raises AttributeError. | **W** |
| fastapi_15280 | drop_file | `docs_src/vibe/tutorial001_py310.py` | `2 files` | `1 files` | **E** | Only a docs example file is missing; library behaviour unchanged. | **E** |
| fastapi_15280 | drop_line | `docs_src/vibe/tutorial001_py310.py` | `app = FastAPI()` | `<deleted>` | **W** | Docs example crashes (`app` undefined); the docs tests do not import it. | **W** |
| fastapi_15661 | bool_swap | `scripts/prepare_release.py` | `exists=True,` | `exists=False,` | **W** | CLI no longer rejects a missing version file up front. | **W** |
| fastapi_15661 | drop_line | `scripts/prepare_release.py` | `file_okay=True,` | `<deleted>` | **E** | `file_okay=True` is already Typer's default. | **E** |
| fastapi_15661 | off_by_one | `scripts/prepare_release.py` | `1,` | `2,` | **?** | `replace(..., 1)` vs `2`: differs only if the header appears twice; the start-of-file check makes that unlikely. | **E** (delegated to Claude 2026-10-28) |
| fastapi_15800 | bool_swap | `fastapi/routing.py` | `] = True,` | `] = False,` | **W** | Default flips: missing frontend directory is no longer detected at app creation. | **W** |
| rich_3052 | bool_swap | `rich/prompt.py` | `case_sensitive: bool = True,` | `case_sensitive: bool = False,` | **W** | Prompt becomes case-insensitive by default: a public behaviour change. | **W** |
| rich_3052 | drop_line | `rich/prompt.py` | `case_sensitive=False,` | `<deleted>` | **E** | Only the `__main__` demo loses its argument; library unchanged. | **E** |
| rich_3061 | flip_compare | `rich/text.py` | `tab_size: int = console.tab_size if self.tab_size is No` | `tab_size: int = console.tab_size if self.tab_size is no` | **W** | Inverted None check: uses `None` as tab size when unset, and ignores an explicit tab size. | **W** |
| rich_3061 | return_none | `rich/text.py` | `return self` | `return None` | **W** | `Span.extend(0)` returns None instead of the span; callers break. | **W** |
| rich_3180 | bool_swap | `rich/_wrap.py` | `def divide_line(text: str, width: int, fold: bool = Tru` | `def divide_line(text: str, width: int, fold: bool = Fal` | **?** | Default `fold` flips; harmless if every caller passes `fold` explicitly (Rich's own callers do), breaking for external callers. | **E** (delegated to Claude 2026-10-28) |
| rich_3180 | off_by_one | `rich/_wrap.py` | `cell_offset = 0` | `cell_offset = 1` | **W** | Line-wrap offset starts at 1: break positions shift. | **W** |
| rich_3468 | bool_swap | `rich/console.py` | `self.quiet = True` | `self.quiet = False` | **?** | `quiet` stays False during broken-pipe exit; only matters if something writes before exit. | **?** (delegated to Claude 2026-10-28) |
| rich_3506 | off_by_one | `rich/segment.py` | `pos = int((cut / cell_length) * (len(text))) - 1` | `pos = int((cut / cell_length) * (len(text))) - 2` | **E** | `pos` is only a starting guess; the following loop walks to the right cut point. | **E** |
| rich_3535 | drop_file | `rich/segment.py` | `2 files` | `1 files` | **W** | Drops the `assert cut >= 0` guard (and docstring): negative cuts no longer rejected. | **W** |
| rich_3535 | drop_line | `rich/segment.py` | `cut (int): Offset within the segment to cut.` | `<deleted>` | **E** | Docstring line (hunk began inside a docstring, so the generator's docstring filter missed it). | **E** |
| rich_3675 | drop_file | `rich/diagnose.py` | `2 files` | `1 files` | **W** | Diagnose report omits the reordered/new env vars (`TTY_COMPATIBLE`); untested `pragma: no cover` code. | **W** |
| rich_3676 | bool_swap | `rich/default_styles.py` | `"traceback.note": Style(color="green", bold=True),` | `"traceback.note": Style(color="green", bold=False),` | **W** | Cosmetic: traceback notes lose bold styling. | **W** |
| rich_3676 | drop_line | `rich/traceback.py` | `notes=notes,` | `<deleted>` | **W** | Exception notes are no longer passed on, so they are not shown. | **W** |
| rich_3772 | bool_swap | `rich/traceback.py` | `exc_value, "__suppress_context__", False` | `exc_value, "__suppress_context__", True` | **E** | Every exception has `__suppress_context__`, so the getattr default is never used. | **E** |
| rich_3772 | drop_line | `rich/traceback.py` | `exc_type = cause.__class__` | `<deleted>` | **W** | Chained exception shows the outer type with the inner value. | **W** |
| rich_3777 | bool_swap | `rich/console.py` | `force_interactive = False` | `force_interactive = True` | **W** | `TTY_INTERACTIVE=0` now forces interactive mode, the opposite of intended. | **W** |
| rich_3777 | drop_file | `rich/diagnose.py` | `2 files` | `1 files` | **W** | Diagnose report omits `TTY_INTERACTIVE`; untested `pragma: no cover` code. | **W** |
| rich_3894 | drop_line | `rich/_inspect.py` | `qualname = getattr(obj, "__name__", name)` | `<deleted>` | **W** | Falls back to `name` instead of `obj.__name__`: wrong name displayed. | **W** |
| rich_3930 | drop_line | `rich/_unicode_data/unicode12-1-0.py` | `"◻",` | `<deleted>` | **W** | One emoji missing from the width table: wrong cell width for it. | **W** |
| rich_3930 | off_by_one | `rich/_unicode_data/unicode17-0-0.py` | `(3636, 3642, 0),` | `(3637, 3642, 0),` | **W** | Range starts one code point late: wrong width for U+0E34. | **W** |
| rich_3934 | off_by_one | `rich/live_render.py` | `return 0` | `return 1` | **W** | Height 1 instead of 0 when nothing was rendered. | **W** |
| rich_3935 | flip_compare | `rich/table.py` | `if column_index == 0:` | `if column_index != 0:` | **W** | Inverted check: removes left padding on every column except the first. | **W** |
| rich_4075 | bool_swap | `rich/console.py` | `styles: bool = False,` | `styles: bool = True,` | **W** | `save_text` saves styles by default: output format changes. | **W** |

## Final verdicts (2026-10-28)

Owner accepted the 32 clear suggestions and delegated the 3 judgment calls: fastapi_15661 off_by_one -> E (start-of-file check makes 1 vs 2 replacements identical in practice); rich_3180 bool_swap -> E (`rich/_wrap.py` is private and every caller passes `fold`); rich_3468 bool_swap -> ? (depends on writes during broken-pipe exit).

**Final: W 24, E 10, ? 1** (of 35 escaped). Tests miss a real bug in **24/163 = 14.7%** of planted bugs; upper bound counting ? = **25/163 = 15.3%** (raw escape rate 35/163 = 21.5%).
