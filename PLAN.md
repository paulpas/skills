# Skill-Router Container Diagnosis

## What the logs show

The container is in a **rapid-fire sync storm**. In the last ~10 minutes the logs contain:

- **8,817 lines** total
- **7,053 sync attempts**
- **3,139 sync failures**

Two recurring git errors keep appearing:

```
fatal: shallow file has changed since we read it
fatal: Unable to create '/cache/skills/.git/index.lock': File exists.
fatal: Unable to create '/cache/skills/.git/shallow.lock': File exists.
```

---

## Root cause (three compounding bugs)

### Bug 1 — Dual timer registration

Env var: `SKILL_SYNC_INTERVAL="3600"` — intended as **3600 seconds (1 hour)**.

In `agent-skill-routing-system/src/index.ts:571,599`:
```ts
const syncIntervalMs = parseInt(process.env.SKILL_SYNC_INTERVAL || '3600', 10) * 1000;
```
That correctly multiplies by 1000 → 3,600,000 ms (1 hour). **The periodic timer interval itself is fine.**

But log timestamps show **dozens of "Syncing skills from GitHub" calls per second**. That's not the periodic timer. It comes from `GitHubSkillLoader.startSync()` being invoked, **plus** the fallback path in `index.ts:622–627` is starting `startSync()` even when the *primary* remote-index path also has its own periodic timer (`remoteIndexSyncTimer`). When the remote index path fails on first fetch, both paths register timers, AND `router.reloadSkills()` re-triggers another sync each time.

### Bug 2 — Concurrent git operations on the same cache dir

`GitHubSkillLoader.pull()` (`GitHubSkillLoader.ts:103-108`) has **no mutex** — every overlapping invocation races on the same `.git/` dir:

```ts
private async pull(): Promise<void> {
  await execFileAsync('git', ['-C', this.cacheDir, 'fetch', '--depth=1', 'origin', 'main']);
  await execFileAsync('git', ['-C', this.cacheDir, 'reset', '--hard', 'origin/main']);
}
```

Once one `--depth=1 fetch` runs while another is mid-flight, the shallow file mutates and corrupts subsequent fetches:

```
fatal: Unable to create '/cache/skills/.git/index.lock': File exists.
Another git process seems to be running in this repository...
fatal: shallow file has changed since we read it
```

### Bug 3 — Skill count oscillation

Skill counts keep changing: `452 → 482 → 439 → 432 → 450 → 480 → 441 → 428…`

Every reload reads `/app/skills` (your local bind-mount, read-only) **plus** `/cache/skills` (the volume). Different counts on each scan suggests scans race against partial writes/resets in `/cache/skills`. This confirms concurrent reloads stomping on each other.

---

## Configuration changes needed

### Keep GitHub sync but stop the storm

If you want the container to auto-pull from GitHub:

1. **Verify the remote index path returns 200** so the fallback git-clone path is never entered:
   ```bash
   curl -sI https://raw.githubusercontent.com/paulpas/skills/main/skills-index.json
   ```
   If it 404s, the code falls into the broken git-clone path.

2. **Code fix required** (not just config): `GitHubSkillLoader.pull()` needs a mutex so overlapping calls serialize. Patch:
   - Add a `private syncing: Promise<void> | null = null` (or a flag) to `GitHubSkillLoader`.
   - In `pull()`, await any in-flight sync rather than launching a parallel git operation.
   - Remove `.git/*.lock` files and re-clone `/cache/skills` if a corrupt state is detected at startup.

3. **The cache volume is corrupted right now**, so even after a fix, the existing `skill-router-cache` volume contains a half-written shallow repo. You'd need:
   ```bash
   docker stop skill-router
   docker volume rm skill-router-cache
   ```

---

---

## Execution plan

1. **Stop the container:** `docker stop skill-router`
3. **Optionally clear the corrupted cache:** `docker volume rm skill-router-cache` (only relevant if you ever flip back to Option B).
4. **Restart** the container with the new env.
5. **Verify the storm is gone:**
   ```bash
   docker logs skill-router --tail 100 | grep -ic "github sync failed"
   ```
   Expected: `0`.
6. **Confirm normal startup:** look for `[INDEX] Using local directory scan (GITHUB_SKILLS_ENABLED=false)` and a single `Loaded N skills from /app/skills` line.
7. **Test `/reload`** still works for picking up new local skills:
   ```bash
   curl -X POST http://localhost:3000/reload
   ```

---

## Relevant environment (for reference)

```
GITHUB_SKILLS_ENABLED=true
SKILL_SYNC_INTERVAL=3600
SKILL_CACHE_DIR=/cache/skills
SKILLS_DIRECTORY=/app/skills
GITHUB_SKILLS_REPO=https://github.com/paulpas/skills
GITHUB_RAW_BASE_URL=https://raw.githubusercontent.com/paulpas/skills/main
```

## Mounts

```
/app/skills   ← bind-mount (read-only) from /Users/ppasika/git/agent-skill-router/skills
/cache        ← named volume skill-router-cache (corrupted)
```

## Code references

- `agent-skill-routing-system/src/skills/GitHubSkillLoader.ts:103-108` — unsafe `pull()` (no mutex)
- `agent-skill-routing-system/src/index.ts:571` — primary periodic timer
- `agent-skill-routing-system/src/index.ts:599` — fallback path interval parsing
- `agent-skill-routing-system/src/index.ts:622-627` — second `startSync()` registration
- `agent-skill-routing-system/src/index.ts:616-620` — `GITHUB_SKILLS_ENABLED=false` branch

