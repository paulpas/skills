export interface GitHubSkillLoaderConfig {
    /** Public GitHub repo URL, e.g. https://github.com/paulpas/skills */
    repoUrl: string;
    /** Local directory to clone/cache the repo into */
    cacheDir: string;
    /** Sync interval in milliseconds (default: 3600000 = 1 hour) */
    syncIntervalMs?: number;
    /** Optional GitHub token for private repos or higher rate limits */
    githubToken?: string;
}
export declare class GitHubSkillLoader {
    private repoUrl;
    private cacheDir;
    private syncIntervalMs;
    private githubToken;
    private syncTimer;
    private logger;
    private syncing;
    constructor(config: GitHubSkillLoaderConfig);
    /** Remove stale .git lock files that may remain from previous crashes. */
    private cleanupStaleLocks;
    /** Clone the repo if needed, pull if already cloned. Call on startup. */
    initialize(): Promise<void>;
    /** Start background sync. Calls onUpdate() after each successful pull. */
    startSync(onUpdate: () => Promise<void>): void;
    /** Stop background sync. */
    stopSync(): void;
    /** Trigger an immediate pull + reload (used by /reload endpoint). */
    syncNow(onUpdate: () => Promise<void>): Promise<void>;
    /** Return the local path where SKILL.md files live after cloning. */
    getSkillsDir(): string;
    private isCloned;
    private clone;
    /** Execute git command with retry and exponential backoff. */
    private runGitCommand;
    private pull;
    /** Pull with retry logic and mutex protection. */
    private pullWithRetry;
    /** Inject token into HTTPS URL for authenticated access if provided. */
    private authUrl;
}
//# sourceMappingURL=GitHubSkillLoader.d.ts.map