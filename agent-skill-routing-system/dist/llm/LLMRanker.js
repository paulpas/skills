"use strict";
// LLM Ranker - ranks skill candidates using OpenAI, Anthropic, or llama.cpp
Object.defineProperty(exports, "__esModule", { value: true });
exports.LLMRanker = void 0;
const Logger_js_1 = require("../observability/Logger.js");
class LLMRanker {
    config;
    logger;
    constructor(config = {}) {
        const provider = process.env.LLM_PROVIDER || config.provider || 'openai';
        this.config = {
            provider,
            apiKey: config.apiKey || process.env.OPENAI_API_KEY || '',
            anthropicApiKey: config.anthropicApiKey || process.env.ANTHROPIC_API_KEY || '',
            llamacppBaseUrl: config.llamacppBaseUrl || process.env.LLAMACPP_BASE_URL || 'http://localhost:8080',
            model: config.model || process.env.LLM_MODEL || this.defaultModel(provider),
            temperature: config.temperature ?? 0.1,
            maxTokens: config.maxTokens ?? 1000,
            maxCandidates: config.maxCandidates ?? 10,
        };
        this.logger = new Logger_js_1.Logger('LLMRanker', { level: 'info', includePayloads: false });
        this.logger.info(`LLMRanker initialized`, { provider: this.config.provider, model: this.config.model });
    }
    defaultModel(provider) {
        switch (provider) {
            case 'anthropic': return 'claude-3-5-haiku-20241022';
            case 'llamacpp': return 'local-model';
            default: return 'gpt-4o-mini';
        }
    }
    async rankCandidates(task, candidates) {
        if (candidates.length === 0)
            return [];
        const limited = candidates.slice(0, this.config.maxCandidates);
        const prompt = this.buildRankingPrompt(task, limited);
        const response = await this.callLLM(prompt);
        const rankings = this.parseRankingResponse(response, limited.map(c => c.metadata.name));
        return rankings.map((ranking, index) => ({
            name: ranking.skillName,
            score: ranking.score,
            role: index === 0 ? 'primary' : 'supporting',
            reasoning: ranking.reason,
        }));
    }
    buildRankingPrompt(task, candidates) {
        const candidatesInfo = candidates
            .map((c, i) => `${i + 1}. ${c.metadata.name}\n   Category: ${c.metadata.category}\n   Description: ${c.metadata.description}\n   Tags: ${c.metadata.tags.join(', ')}`)
            .join('\n\n');
        return `You are a skill router for an agentic coding system. Given a task, rank the most appropriate skills.

Task: ${task}

Available Skills:
${candidatesInfo}

Instructions:
1. Rank skills from most to least relevant
2. Assign a relevance score (0.0-1.0)
3. Provide a brief reason for each ranking
4. Only include skills with score >= 0.5

Output format (JSON only, no extra text):
{
  "rankings": [
    {"skillName": "skill-name", "score": 0.95, "reason": "Brief reason"}
  ]
}`;
    }
    async callLLM(prompt) {
        try {
            switch (this.config.provider) {
                case 'anthropic': return await this.callAnthropic(prompt);
                case 'llamacpp': return await this.callOpenAICompatible(prompt, this.config.llamacppBaseUrl);
                default: return await this.callOpenAICompatible(prompt, 'https://api.openai.com');
            }
        }
        catch (error) {
            this.logger.error('LLM call failed, using fallback ranking', {
                provider: this.config.provider,
                error: error instanceof Error ? error.message : String(error),
            });
            return this.fallbackRanking();
        }
    }
    /** OpenAI-compatible endpoint (used for both openai and llamacpp) */
    async callOpenAICompatible(prompt, baseUrl) {
        const apiKey = this.config.provider === 'llamacpp'
            ? (this.config.apiKey || 'no-key') // llama.cpp doesn't require a real key
            : this.config.apiKey;
        const response = await fetch(`${baseUrl}/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`,
            },
            body: JSON.stringify({
                model: this.config.model,
                messages: [
                    { role: 'system', content: 'You are a precise skill router. Always output valid JSON.' },
                    { role: 'user', content: prompt },
                ],
                temperature: this.config.temperature,
                max_tokens: this.config.maxTokens,
            }),
        });
        if (!response.ok) {
            const err = await response.text();
            throw new Error(`${baseUrl} API error ${response.status}: ${err}`);
        }
        const data = await response.json();
        return data.choices[0].message.content;
    }
    /** Anthropic Messages API */
    async callAnthropic(prompt) {
        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': this.config.anthropicApiKey,
                'anthropic-version': '2023-06-01',
            },
            body: JSON.stringify({
                model: this.config.model,
                max_tokens: this.config.maxTokens,
                system: 'You are a precise skill router. Always output valid JSON.',
                messages: [{ role: 'user', content: prompt }],
            }),
        });
        if (!response.ok) {
            const err = await response.text();
            throw new Error(`Anthropic API error ${response.status}: ${err}`);
        }
        const data = await response.json();
        const textBlock = data.content.find(b => b.type === 'text');
        if (!textBlock)
            throw new Error('Anthropic response contained no text block');
        return textBlock.text;
    }
    parseRankingResponse(response, availableSkills) {
        try {
            const jsonMatch = response.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                const json = JSON.parse(jsonMatch[0]);
                return (json.rankings || []).filter(r => availableSkills.includes(r.skillName));
            }
        }
        catch (error) {
            this.logger.warn('Failed to parse LLM ranking response as JSON', {
                error: error instanceof Error ? error.message : String(error),
            });
        }
        // line-by-line fallback
        const rankings = [];
        for (const line of response.split('\n')) {
            const match = line.match(/(\d+)\.\s+(\S+)\s+score:\s*([\d.]+)\s*reason:\s*(.+)/i);
            if (match) {
                const [, , skillName, score, reason] = match;
                if (availableSkills.includes(skillName)) {
                    rankings.push({ skillName, score: parseFloat(score) || 0, reason: reason.trim(), confidence: 0.8 });
                }
            }
        }
        return rankings;
    }
    fallbackRanking() {
        return JSON.stringify({ rankings: [{ skillName: 'fallback', score: 0.5, reason: 'LLM unavailable' }] });
    }
    getModel() { return this.config.model; }
    getProvider() { return this.config.provider; }
}
exports.LLMRanker = LLMRanker;
//# sourceMappingURL=LLMRanker.js.map