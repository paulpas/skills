"use strict";
// GitHubSkillLoader - clones and syncs skills from a public GitHub repository
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.GitHubSkillLoader = void 0;
const child_process_1 = require("child_process");
const util_1 = require("util");
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const Logger_1 = require("../observability/Logger");
const execFileAsync = (0, util_1.promisify)(child_process_1.execFile);
class GitHubSkillLoader {
    repoUrl;
    cacheDir;
    syncIntervalMs;
    githubToken;
    syncTimer = null;
    logger;
    syncing = null;
    constructor(config) {
        this.repoUrl = config.repoUrl;
        this.cacheDir = config.cacheDir;
        this.syncIntervalMs = config.syncIntervalMs ?? 3600000;
        this.githubToken = config.githubToken ?? '';
        this.logger = new Logger_1.Logger('GitHubSkillLoader');
        this.cleanupStaleLocks();
    }
    /** Remove stale .git lock files that may remain from previous crashes. */
    cleanupStaleLocks() {
        const gitDir = path_1.default.join(this.cacheDir, '.git');
        const lockFiles = ['index.lock', 'shallow.lock'];
        for (const lockFile of lockFiles) {
            const lockPath = path_1.default.join(gitDir, lockFile);
            fs_1.default.promises.unlink(lockPath).catch(() => {
                // Silent cleanup - lock files may not exist
            });
        }
    }
    /** Clone the repo if needed, pull if already cloned. Call on startup. */
    async initialize() {
        if (await this.isCloned()) {
            this.logger.info('Skills cache exists, syncing (fetch + reset)', { dir: this.cacheDir });
            await this.pull();
        }
        else {
            this.logger.info('Cloning skills repository', { url: this.repoUrl, to: this.cacheDir });
            await this.clone();
        }
        this.logger.info('GitHub skills initialized', { dir: this.cacheDir });
    }
    /** Start background sync. Calls onUpdate() after each successful pull. */
    startSync(onUpdate) {
        if (this.syncTimer)
            return; // already running
        this.syncTimer = setInterval(async () => {
            try {
                this.logger.info('Syncing skills from GitHub');
                await this.pull();
                this.logger.info('Sync complete, reloading skills');
                await onUpdate();
            }
            catch (err) {
                this.logger.error('GitHub sync failed', {
                    error: err instanceof Error ? err.message : String(err),
                });
            }
        }, this.syncIntervalMs);
        this.logger.info('Background GitHub sync started', { intervalMs: this.syncIntervalMs });
    }
    /** Stop background sync. */
    stopSync() {
        if (this.syncTimer) {
            clearInterval(this.syncTimer);
            this.syncTimer = null;
            this.logger.info('GitHub sync stopped');
        }
    }
    /** Trigger an immediate pull + reload (used by /reload endpoint). */
    async syncNow(onUpdate) {
        await this.pull();
        await onUpdate();
    }
    /** Return the local path where SKILL.md files live after cloning. */
    getSkillsDir() {
        return this.cacheDir;
    }
    async isCloned() {
        try {
            await fs_1.default.promises.access(path_1.default.join(this.cacheDir, '.git'));
            return true;
        }
        catch {
            return false;
        }
    }
    async clone() {
        await fs_1.default.promises.mkdir(path_1.default.dirname(this.cacheDir), { recursive: true });
        const url = this.authUrl(this.repoUrl);
        await execFileAsync('git', ['clone', '--depth=1', url, this.cacheDir]);
    }
    /** Execute git command with retry and exponential backoff. */
    async runGitCommand(args, maxRetries = 3) {
        const baseDelay = 100; // 100ms base delay
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                await execFileAsync('git', args);
                return; // Success
            }
            catch (err) {
                if (attempt === maxRetries) {
                    // Re-throw on final attempt
                    throw new Error(`Git command failed after ${maxRetries} attempts: ${String(err)}`);
                }
                const delay = baseDelay * Math.pow(2, attempt - 1);
                this.logger.warn('Git command failed, retrying', {
                    args: args.join(' '),
                    attempt,
                    maxRetries,
                    delayMs: delay,
                    error: err instanceof Error ? err.message : String(err),
                });
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    async pull() {
        // Early Exit: If already syncing, await existing operation
        if (this.syncing) {
            this.logger.info('Sync already in progress, waiting for completion');
            await this.syncing;
            return;
        }
        // Set syncing flag to prevent concurrent operations
        this.syncing = this.pullWithRetry();
        try {
            await this.syncing;
        }
        finally {
            // Clear syncing flag after completion (success or failure)
            this.syncing = null;
        }
    }
    /** Pull with retry logic and mutex protection. */
    async pullWithRetry() {
        // Fetch latest without requiring fast-forward — handles force pushes and rebased history
        await this.runGitCommand(['-C', this.cacheDir, 'fetch', '--depth=1', 'origin', 'main']);
        // Hard reset to remote HEAD — always wins, never diverges
        await this.runGitCommand(['-C', this.cacheDir, 'reset', '--hard', 'origin/main']);
    }
    /** Inject token into HTTPS URL for authenticated access if provided. */
    authUrl(url) {
        if (!this.githubToken)
            return url;
        return url.replace('https://', `https://${this.githubToken}@`);
    }
}
exports.GitHubSkillLoader = GitHubSkillLoader;
//# sourceMappingURL=GitHubSkillLoader.js.map