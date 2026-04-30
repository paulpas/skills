import type { SkillDefinition, SkillRankingResult } from '../core/types.js';
export type LLMProvider = 'openai' | 'anthropic' | 'llamacpp';
export interface LLMRankerConfig {
    provider?: LLMProvider;
    /** OpenAI API key (required for openai provider; also used for embeddings) */
    apiKey?: string;
    /** Anthropic API key (required for anthropic provider) */
    anthropicApiKey?: string;
    /** llama.cpp base URL e.g. http://localhost:8080 (required for llamacpp provider) */
    llamacppBaseUrl?: string;
    model?: string;
    temperature?: number;
    maxTokens?: number;
    maxCandidates?: number;
}
export declare class LLMRanker {
    private config;
    private logger;
    private rankingCache;
    private inputTokens;
    private outputTokens;
    constructor(config?: Partial<LLMRankerConfig>);
    /**
     * Deterministic hash key for a task + candidate set combination.
     * Used to avoid redundant LLM calls for identical routing requests.
     */
    private hashKey;
    private defaultModel;
    rankCandidates(task: string, candidates: SkillDefinition[]): Promise<SkillRankingResult[]>;
    private buildRankingPrompt;
    private callLLM;
    /** OpenAI-compatible endpoint (used for both openai and llamacpp) */
    private callOpenAICompatible;
    /** Anthropic Messages API */
    private callAnthropic;
    private parseRankingResponse;
    private fallbackRanking;
    getModel(): string;
    getProvider(): LLMProvider;
    getInputTokens(): number;
    getOutputTokens(): number;
    /**
     * Reset token counters - useful for testing or fresh sessions
     */
    resetTokenCounters(): void;
}
//# sourceMappingURL=LLMRanker.d.ts.map