## Per config

| Config | Tasks | Resolved | Rate (95% CI) | Used any graph tool | Mean tool calls | Median time (s) | Mean tokens | Mean first source edit (call #) | Errors |
|---|---|---|---|---|---|---|---|---|---|
| n4 | 32 | 14 | 44% (28%–61%) | 3/32 | 44.2 | 370 | 415,652 | 20.0 | 3 |

## Graph tool usage

Calls per run, and the share of runs that used the tool at least once.

| Config | get_code_neighbors | search_similar_code | get_code_subgraph | read_file | run_command | sub-agent |
|---|---|---|---|---|---|---|
| n4 | 0.2 (3/32) | 0.0 (0/32) | 0.0 (0/32) | 11.6 (32/32) | 15.2 (32/32) | 0.0 (0/32) |

## Task x config

✅ resolved, ❌ not resolved, · not run (tool calls in brackets)

| Task | n4 |
|---|---|
| fastapi_13920 | ❌ (50) |
| fastapi_14258 | ❌ (21) |
| fastapi_14301 | ✅ (18) |
| fastapi_14306 | ❌ (63) |
| fastapi_14372 | ✅ (23) |
| fastapi_14419 | ✅ (60) |
| fastapi_14448 | ❌ (20) |
| fastapi_14458 | ✅ (18) |
| fastapi_14463 | ❌ (89) |
| fastapi_14479 | ❌ (38) |
| fastapi_14487 | ❌ (59) |
| fastapi_14492 | ✅ (11) |
| fastapi_14786 | ✅ (37) |
| fastapi_14794 | ✅ (15) |
| fastapi_14873 | ✅ (35) |
| fastapi_14986 | ❌ (18) |
| fastapi_15280 | ❌ (66) |
| fastapi_15588 | ❌ (44) |
| fastapi_15589 | ❌ (61) |
| fastapi_15661 | ❌ (18) |
| fastapi_5077 | ✅ (40) |
| fastapi_5624 | ✅ (32) |
| fastapi_9425 | ✅ (44) |
| fastapi_9555 | ✅ (31) |
| fastapi_9753 | ✅ (30) |
| rich_3718 | ❌ (200) |
| rich_3934 | ❌ (62) |
| rich_3953 | ❌ (26) |
| rich_4006 | ❌ (19) |
| rich_4075 | ❌ (61) |
| rich_4076 | ❌ (65) |
| rich_4077 | ✅ (39) |
