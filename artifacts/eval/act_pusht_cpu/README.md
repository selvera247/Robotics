# PushT ACT eval artifacts (CPU smoke)

From `lerobot-eval` of Hub policy `wlinhugging/lerobot-pusht-act-policy` on `--env.type=pusht` (5 episodes, success rate 0%).

| File | Notes |
| --- | --- |
| `videos/eval_episode_0.mp4` | Best episode (max reward ~0.64) |
| `videos/eval_episode_4.mp4` | Worst episode (max reward ~0.20) |
| `eval_info.json` | Full metrics for all 5 episodes |

Only the best/worst videos are checked in to keep the tree small. Re-run eval locally to regenerate episodes 1–3 if needed.
