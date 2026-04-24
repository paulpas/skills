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
            temperature: config.temperature ?? 0,
            maxTokens: config.maxTokens ?? 400,
            maxCandidates: config.maxCandidates ?? 10,
        };
        this.logger = new Logger_js_1.Logger('LLMRanker');
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
        // Log what we're sending to the LLM
        this.logger.info('Sending ranking request to LLM', {
            provider: this.config.provider,
            model: this.config.model,
            task: task.slice(0, 120),
            candidateCount: limited.length,
            candidates: limited.map(c => c.metadata.name),
        });
        const t0 = Date.now();
        const response = await this.callLLM(prompt);
        const durationMs = Date.now() - t0;
        // Log raw LLM response
        this.logger.debug('LLM raw response', {
            durationMs,
            responseLength: response.length,
            response: response.slice(0, 500), // truncate very long responses
        });
        const rankings = this.parseRankingResponse(response, limited.map(c => c.metadata.name));
        // Log parsed rankings
        this.logger.info('LLM ranking result', {
            durationMs,
            rankedCount: rankings.length,
            rankings: rankings.map(r => ({ skill: r.skillName, score: r.score, reason: r.reason?.slice(0, 80) })),
        });
        return rankings.map((ranking, index) => ({
            name: ranking.skillName,
            score: ranking.score,
            role: index === 0 ? 'primary' : 'supporting',
            reasoning: ranking.reason,
        }));
    }
    buildRankingPrompt(task, candidates) {
        const candidateLines = candidates
            .map((c, i) => `${i + 1}. ${c.metadata.name}: ${c.metadata.description}`)
            .join('\n');
        return `Task: "${task}"

Candidate skills:
${candidateLines}

Rank these skills by relevance to the task.

Return ONLY this JSON (no prose, no markdown, no explanation):
{
  "rankings": [
    {"skillName": "<name>", "score": 0.0, "reason": "<10 words max>"}
  ]
}

Rules:
- score 0.0-1.0 (1.0 = perfect match)
- reason must be 10 words or fewer
- include only skills with score >= 0.3
- order by score descending`;
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
                model: this.config.model,
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
                    { role: 'system', content: 'You are a skill-routing classifier. Respond ONLY with valid JSON. No explanation, no markdown, no preamble. Output nothing except the JSON object requested.' },
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
                system: 'You are a skill-routing classifier. Respond ONLY with valid JSON. No explanation, no markdown, no preamble. Output nothing except the JSON object requested.',
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