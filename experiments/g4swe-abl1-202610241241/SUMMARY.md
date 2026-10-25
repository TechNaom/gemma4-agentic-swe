## Per config

| Config | Tasks | Resolved | Rate (95% CI) | Used any graph tool | Mean tool calls | Median time (s) | Mean tokens | Mean first source edit (call #) | Errors |
|---|---|---|---|---|---|---|---|---|---|
| k0 | 68 | 34 | 50% (38%–62%) | 0/68 | 37.8 | 404 | 348,123 | 18.1 | 6 |
| k4 | 33 | 16 | 48% (33%–65%) | 0/33 | 37.3 | 383 | 352,533 | 20.2 | 1 |

## Graph tool usage

Calls per run, and the share of runs that used the tool at least once.

| Config | get_code_neighbors | search_similar_code | get_code_subgraph | read_file | run_command | sub-agent |
|---|---|---|---|---|---|---|
| k0 | 0.0 (0/68) | 0.0 (0/68) | 0.0 (0/68) | 11.7 (68/68) | 15.2 (68/68) | 0.0 (0/68) |
| k4 | 0.0 (0/33) | 0.0 (0/33) | 0.0 (0/33) | 11.6 (33/33) | 15.1 (33/33) | 0.0 (0/33) |

## Paired comparison with k0

Same tasks for both configs. *Only base* / *only config*: tasks solved by one and not the other.
p: exact McNemar test on those discordant tasks (p < 0.05 suggests a real difference).

| Config | Tasks paired | Both | Only k0 | Only config | Neither | Δ resolved | p |
|---|---|---|---|---|---|---|---|
| k4 | 33 | 15 | 2 | 1 | 15 | -1 | 1.00 |

## Task x config

✅ resolved, ❌ not resolved, · not run (tool calls in brackets)

| Task | k0 | k4 |
|---|---|---|
| fastapi_11194 | ✅ (62) | · |
| fastapi_13537 | ✅ (16) | · |
| fastapi_13920 | ❌ (61) | ❌ (32) |
| fastapi_14258 | ❌ (43) | ❌ (41) |
| fastapi_14301 | ✅ (85) | ✅ (20) |
| fastapi_14306 | ❌ (57) | ❌ (88) |
| fastapi_14372 | ✅ (40) | ✅ (33) |
| fastapi_14419 | ✅ (28) | ❌ (63) |
| fastapi_14448 | ❌ (39) | ❌ (31) |
| fastapi_14458 | ✅ (16) | ✅ (17) |
| fastapi_14463 | ✅ (14) | ✅ (15) |
| fastapi_14479 | ❌ (17) | ❌ (23) |
| fastapi_14487 | ❌ (61) | ❌ (42) |
| fastapi_14492 | ✅ (13) | ✅ (12) |
| fastapi_14616 | ❌ (62) | · |
| fastapi_14786 | ✅ (7) | ✅ (13) |
| fastapi_14794 | ✅ (65) | ✅ (22) |
| fastapi_14873 | ✅ (62) | ✅ (36) |
| fastapi_14986 | ❌ (28) | ❌ (34) |
| fastapi_15280 | ❌ (60) | ❌ (69) |
| fastapi_15588 | ❌ (19) | ❌ (26) |
| fastapi_15589 | ❌ (60) | ❌ (64) |
| fastapi_15661 | ❌ (34) | ❌ (43) |
| fastapi_15800 | ❌ (36) | · |
| fastapi_5077 | ✅ (13) | ✅ (51) |
| fastapi_5624 | ✅ (83) | ✅ (47) |
| fastapi_9425 | ✅ (30) | ✅ (32) |
| fastapi_9555 | ✅ (17) | ✅ (37) |
| fastapi_9753 | ✅ (62) | ✅ (30) |
| rich_2725 | ✅ (16) | · |
| rich_2943 | ✅ (26) | · |
| rich_3006 | ✅ (34) | · |
| rich_3043 | ✅ (45) | · |
| rich_3052 | ❌ (11) | · |
| rich_3061 | ❌ (29) | · |
| rich_3063 | ✅ (33) | · |
| rich_3067 | ✅ (27) | · |
| rich_3105 | ❌ (64) | · |
| rich_3180 | ✅ (33) | · |
| rich_3278 | ✅ (21) | · |
| rich_3454 | ✅ (56) | · |
| rich_3468 | ❌ (30) | · |
| rich_3470 | ❌ (40) | · |
| rich_3471 | ❌ (29) | · |
| rich_3480 | ✅ (30) | · |
| rich_3506 | ❌ (47) | · |
| rich_3518 | ✅ (22) | · |
| rich_3521 | ❌ (21) | · |
| rich_3535 | ❌ (13) | · |
| rich_3675 | ❌ (25) | · |
| rich_3676 | ❌ (35) | · |
| rich_3718 | ✅ (39) | ✅ (18) |
| rich_3772 | ❌ (37) | · |
| rich_3777 | ✅ (53) | · |
| rich_3882 | ✅ (60) | · |
| rich_3894 | ✅ (16) | · |
| rich_3905 | ✅ (12) | · |
| rich_3930 | ❌ (36) | · |
| rich_3934 | ❌ (27) | ❌ (60) |
| rich_3935 | ❌ (56) | · |
| rich_3938 | ❌ (63) | · |
| rich_3942 | ❌ (62) | · |
| rich_3944 | ✅ (32) | ❌ (30) |
| rich_3953 | ❌ (29) | ❌ (17) |
| rich_4006 | ❌ (29) | ❌ (21) |
| rich_4075 | ✅ (46) | ✅ (61) |
| rich_4076 | ❌ (63) | ❌ (60) |
| rich_4077 | ❌ (35) | ✅ (43) |
