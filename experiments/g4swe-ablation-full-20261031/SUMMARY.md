# Full ablation: k0, k4 and n4 (31 Oct 2026)

k0 and the first 33 k4 tasks: abl1 (`../g4swe-abl1-202610241241`). The other 35 k4 tasks: abl3. n4: abl4, stopped by its 4-hour cap after 32 tasks (8 h of GPU quota on 4x L4).

Regenerate: `python -m g4swe.analyze experiments/g4swe-abl1-202610241241/*_agent_k0 experiments/g4swe-abl1-202610241241/*_agent_k4 experiments/g4swe-ablation-full-20261031/*_agent_k4 experiments/g4swe-ablation-full-20261031/*_agent_n4`

## Per config

| Config | Tasks | Resolved | Rate (95% CI) | Used any graph tool | Mean tool calls | Median time (s) | Mean tokens | Mean first source edit (call #) | Errors |
|---|---|---|---|---|---|---|---|---|---|
| k0 | 68 | 34 | 50% (38%–62%) | 0/68 | 37.8 | 404 | 348,123 | 18.1 | 6 |
| k4 | 68 | 32 | 47% (36%–59%) | 4/68 | 40.4 | 408 | 380,144 | 19.7 | 6 |
| n4 | 32 | 14 | 44% (28%–61%) | 3/32 | 44.2 | 370 | 415,652 | 20.0 | 3 |

## Graph tool usage

Calls per run, and the share of runs that used the tool at least once.

| Config | get_code_neighbors | search_similar_code | get_code_subgraph | read_file | run_command | sub-agent |
|---|---|---|---|---|---|---|
| k0 | 0.0 (0/68) | 0.0 (0/68) | 0.0 (0/68) | 11.7 (68/68) | 15.2 (68/68) | 0.0 (0/68) |
| k4 | 0.1 (4/68) | 0.0 (0/68) | 0.0 (0/68) | 11.5 (68/68) | 15.1 (68/68) | 0.0 (0/68) |
| n4 | 0.2 (3/32) | 0.0 (0/32) | 0.0 (0/32) | 11.6 (32/32) | 15.2 (32/32) | 0.0 (0/32) |

## Paired comparison with k0

Same tasks for both configs. *Only base* / *only config*: tasks solved by one and not the other.
p: exact McNemar test on those discordant tasks (p < 0.05 suggests a real difference).

| Config | Tasks paired | Both | Only k0 | Only config | Neither | Δ resolved | p |
|---|---|---|---|---|---|---|---|
| k4 | 68 | 30 | 4 | 2 | 32 | -2 | 0.69 |
| n4 | 32 | 13 | 3 | 1 | 15 | -2 | 0.62 |

## Task x config

✅ resolved, ❌ not resolved, · not run (tool calls in brackets)

| Task | k0 | k4 | n4 |
|---|---|---|---|
| fastapi_11194 | ✅ (62) | ✅ (45) | · |
| fastapi_13537 | ✅ (16) | ✅ (13) | · |
| fastapi_13920 | ❌ (61) | ❌ (32) | ❌ (50) |
| fastapi_14258 | ❌ (43) | ❌ (41) | ❌ (21) |
| fastapi_14301 | ✅ (85) | ✅ (20) | ✅ (18) |
| fastapi_14306 | ❌ (57) | ❌ (88) | ❌ (63) |
| fastapi_14372 | ✅ (40) | ✅ (33) | ✅ (23) |
| fastapi_14419 | ✅ (28) | ❌ (63) | ✅ (60) |
| fastapi_14448 | ❌ (39) | ❌ (31) | ❌ (20) |
| fastapi_14458 | ✅ (16) | ✅ (17) | ✅ (18) |
| fastapi_14463 | ✅ (14) | ✅ (15) | ❌ (89) |
| fastapi_14479 | ❌ (17) | ❌ (23) | ❌ (38) |
| fastapi_14487 | ❌ (61) | ❌ (42) | ❌ (59) |
| fastapi_14492 | ✅ (13) | ✅ (12) | ✅ (11) |
| fastapi_14616 | ❌ (62) | ❌ (61) | · |
| fastapi_14786 | ✅ (7) | ✅ (13) | ✅ (37) |
| fastapi_14794 | ✅ (65) | ✅ (22) | ✅ (15) |
| fastapi_14873 | ✅ (62) | ✅ (36) | ✅ (35) |
| fastapi_14986 | ❌ (28) | ❌ (34) | ❌ (18) |
| fastapi_15280 | ❌ (60) | ❌ (69) | ❌ (66) |
| fastapi_15588 | ❌ (19) | ❌ (26) | ❌ (44) |
| fastapi_15589 | ❌ (60) | ❌ (64) | ❌ (61) |
| fastapi_15661 | ❌ (34) | ❌ (43) | ❌ (18) |
| fastapi_15800 | ❌ (36) | ❌ (51) | · |
| fastapi_5077 | ✅ (13) | ✅ (51) | ✅ (40) |
| fastapi_5624 | ✅ (83) | ✅ (47) | ✅ (32) |
| fastapi_9425 | ✅ (30) | ✅ (32) | ✅ (44) |
| fastapi_9555 | ✅ (17) | ✅ (37) | ✅ (31) |
| fastapi_9753 | ✅ (62) | ✅ (30) | ✅ (30) |
| rich_2725 | ✅ (16) | ✅ (15) | · |
| rich_2943 | ✅ (26) | ✅ (48) | · |
| rich_3006 | ✅ (34) | ✅ (37) | · |
| rich_3043 | ✅ (45) | ✅ (20) | · |
| rich_3052 | ❌ (11) | ✅ (21) | · |
| rich_3061 | ❌ (29) | ❌ (56) | · |
| rich_3063 | ✅ (33) | ❌ (64) | · |
| rich_3067 | ✅ (27) | ✅ (38) | · |
| rich_3105 | ❌ (64) | ❌ (56) | · |
| rich_3180 | ✅ (33) | ❌ (22) | · |
| rich_3278 | ✅ (21) | ✅ (15) | · |
| rich_3454 | ✅ (56) | ✅ (86) | · |
| rich_3468 | ❌ (30) | ❌ (58) | · |
| rich_3470 | ❌ (40) | ❌ (66) | · |
| rich_3471 | ❌ (29) | ❌ (23) | · |
| rich_3480 | ✅ (30) | ✅ (32) | · |
| rich_3506 | ❌ (47) | ❌ (28) | · |
| rich_3518 | ✅ (22) | ✅ (22) | · |
| rich_3521 | ❌ (21) | ❌ (7) | · |
| rich_3535 | ❌ (13) | ❌ (10) | · |
| rich_3675 | ❌ (25) | ❌ (45) | · |
| rich_3676 | ❌ (35) | ❌ (54) | · |
| rich_3718 | ✅ (39) | ✅ (18) | ❌ (200) |
| rich_3772 | ❌ (37) | ❌ (42) | · |
| rich_3777 | ✅ (53) | ✅ (60) | · |
| rich_3882 | ✅ (60) | ✅ (57) | · |
| rich_3894 | ✅ (16) | ✅ (15) | · |
| rich_3905 | ✅ (12) | ✅ (15) | · |
| rich_3930 | ❌ (36) | ❌ (192) | · |
| rich_3934 | ❌ (27) | ❌ (60) | ❌ (62) |
| rich_3935 | ❌ (56) | ❌ (49) | · |
| rich_3938 | ❌ (63) | ❌ (52) | · |
| rich_3942 | ❌ (62) | ❌ (41) | · |
| rich_3944 | ✅ (32) | ❌ (30) | · |
| rich_3953 | ❌ (29) | ❌ (17) | ❌ (26) |
| rich_4006 | ❌ (29) | ❌ (21) | ❌ (19) |
| rich_4075 | ✅ (46) | ✅ (61) | ❌ (61) |
| rich_4076 | ❌ (63) | ❌ (60) | ❌ (65) |
| rich_4077 | ❌ (35) | ✅ (43) | ✅ (39) |
