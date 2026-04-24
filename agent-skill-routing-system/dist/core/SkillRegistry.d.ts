import type { SkillDefinition } from './types.js';
/**
 * Configuration for the skill registry
 */
export interface SkillRegistryConfig {
    /** Single directory or array of directories to load skills from.
     *  When multiple directories are given, skills loaded earlier win on name collision
     *  (i.e. list local mount first so local skills override remote ones). */
    skillsDirectory: string | string[];
    cacheDirectory?: string;
    generateEmbeddings?: boolean;
}
/**
 * Skill Registry - manages all available skills
 */
export declare class SkillRegistry {
    private skills;
    private skillsByCategory;
    private skillsByTag;
    private config;
    private embeddingService;
    private logger;
    /** In-memory cache for on-demand skill content */
    private contentCache;
    constructor(config: SkillRegistryConfig);
    /**
     * Fetch the lightweight skills-index.json from a remote URL and populate the
     * registry with metadata only (no content). Content is fetched on-demand.
     * Falls back gracefully — callers should catch errors and fall back to loadSkills().
     */
    loadFromRemoteIndex(indexUrl: string): Promise<void>;
    /**
     * Fetch the full SKILL.md content for a skill on-demand.
     * Resolution order: memory cache → local disk → GitHub raw → persist to disk.
     */
    getSkillContent(name: string): Promise<string>;
    /** Write skill content to the on-disk content cache (non-fatal on error). */
    private persistSkillContent;
    /**
     * Pre-populate the memory content cache from the on-disk content cache at startup.
     * This avoids a GitHub round-trip for skills accessed since last restart.
     */
    private loadPersistedContentCache;
    /**
     * Load all skills from one or more skill directories.
     * Directories are processed in order; first directory wins on name collision
     * so local skills always override remote ones.
     */
    loadSkills(): Promise<void>;
    /**
     * Load a single skill from a SKILL.md file
     */
    private loadSkillFromFile;
    /**
     * Parse skill metadata from a SKILL.md file with YAML frontmatter
     * Maps OpenCode skill frontmatter fields to SkillMetadata schema
     */
    private parseSkillFromMarkdown;
    /**
     * Validate skill metadata against expected schema
     */
    private isValidSkillMetadata;
    /**
     * Add a skill to the registry
     */
    private addSkill;
    /**
     * Build text for embedding generation from skill metadata
     */
    private buildEmbeddingText;
    /**
     * Generate embeddings for skills that don't have them
     */
    private generateMissingEmbeddings;
    /**
     * Get a skill by name
     */
    getSkill(name: string): SkillDefinition | undefined;
    /**
     * Get all skills
     */
    getAllSkills(): SkillDefinition[];
    /**
     * Get skills by category
     */
    getSkillsByCategory(category: string): SkillDefinition[];
    /**
     * Get skills by tag
     */
    getSkillsByTag(tag: string): SkillDefinition[];
    /**
     * Search skills by category or tag
     */
    searchByCategoryOrTag(searchTerm: string): SkillDefinition[];
    /**
     * Reload all skills
     */
    reload(): Promise<void>;
    /**
     * Get registry statistics
     */
    getStats(): {
        totalSkills: number;
        categories: number;
        tags: number;
        skillsWithoutEmbeddings: number;
    };
    /**
     * Lenient line-by-line frontmatter extractor for YAML that strict parsers reject.
     * Handles: unquoted colons in values, tabs, CRLF line endings, trailing spaces.
     */
    private parseFrontmatterLenient;
    /** Strip surrounding single or double quotes from a YAML scalar value */
    private unquoteFrontmatterValue;
}
//# sourceMappingURL=SkillRegistry.d.ts.map