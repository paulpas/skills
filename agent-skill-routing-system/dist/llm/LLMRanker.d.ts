import type { SkillDefinition, SelectedSkill } from '../core/types.js';
export type LLMProvider = 'openai' | 'anthropic' | 'llamacpp';
export interface LLMRankerConfig {
    provider?: LLMProvider;
    /** OpenAI API key (required for openai provider; also used for embeddings) */
    apiKey?: string;
    /** Anthropic API key (required for anthropic provider) */
    anthropicApiKey?: string;
    /** llama.cpp base URL e.g. http://localhost:8080 (required for llamacpp provider) */
    llamacppBaseUrl?: string;
    model: string;
    temperature?: number;
    maxTokens?: number;
    maxCandidates?: number;
}
export declare class LLMRanker {
    private config;
    private logger;
    constructor(config?: Partial<LLMRankerConfig>);
    private defaultModel;
    rankCandidates(task: string, candidates: SkillDefinition[]): Promise<SelectedSkill[]>;
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
}
//# sourceMappingURL=LLMRanker.d.ts.map