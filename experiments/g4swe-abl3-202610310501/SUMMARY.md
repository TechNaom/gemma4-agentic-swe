## Per config

| Config | Tasks | Resolved | Rate (95% CI) | Used any graph tool | Mean tool calls | Median time (s) | Mean tokens | Mean first source edit (call #) | Errors |
|---|---|---|---|---|---|---|---|---|---|
| k4 | 35 | 16 | 46% (30%–62%) | 4/35 | 43.3 | 460 | 406,178 | 19.1 | 5 |

## Graph tool usage

Calls per run, and the share of runs that used the tool at least once.

| Config | get_code_neighbors | search_similar_code | get_code_subgraph | read_file | run_command | sub-agent |
|---|---|---|---|---|---|---|
| k4 | 0.1 (4/35) | 0.0 (0/35) | 0.0 (0/35) | 11.4 (35/35) | 15.1 (35/35) | 0.0 (0/35) |

## Task x config

✅ resolved, ❌ not resolved, · not run (tool calls in brackets)

| Task | k4 |
|---|---|
| fastapi_11194 | ✅ (45) |
| fastapi_13537 | ✅ (13) |
| fastapi_14616 | ❌ (61) |
| fastapi_15800 | ❌ (51) |
| rich_2725 | ✅ (15) |
| rich_2943 | ✅ (48) |
| rich_3006 | ✅ (37) |
| rich_3043 | ✅ (20) |
| rich_3052 | ✅ (21) |
| rich_3061 | ❌ (56) |
| rich_3063 | ❌ (64) |
| rich_3067 | ✅ (38) |
| rich_3105 | ❌ (56) |
| rich_3180 | ❌ (22) |
| rich_3278 | ✅ (15) |
| rich_3454 | ✅ (86) |
| rich_3468 | ❌ (58) |
| rich_3470 | ❌ (66) |
| rich_3471 | ❌ (23) |
| rich_3480 | ✅ (32) |
| rich_3506 | ❌ (28) |
| rich_3518 | ✅ (22) |
| rich_3521 | ❌ (7) |
| rich_3535 | ❌ (10) |
| rich_3675 | ❌ (45) |
| rich_3676 | ❌ (54) |
| rich_3772 | ❌ (42) |
| rich_3777 | ✅ (60) |
| rich_3882 | ✅ (57) |
| rich_3894 | ✅ (15) |
| rich_3905 | ✅ (15) |
| rich_3930 | ❌ (192) |
| rich_3935 | ❌ (49) |
| rich_3938 | ❌ (52) |
| rich_3942 | ❌ (41) |
