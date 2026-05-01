import { EmbeddingResponse } from '../core/types';
export type EmbeddingProvider = 'openai' | 'llamacpp';
/**
 * Configuration for the embedding service
 */
export interface EmbeddingServiceConfig {
    provider?: EmbeddingProvider;
    apiKey?: string;
    llamacppBaseUrl?: string;
    model?: string;
    dimensions: number;
    cacheDirectory?: string;
    batchSize: number;
}
/**
 * Embedding service supporting OpenAI and llama.cpp providers
 */
export declare class EmbeddingService {
    private config;
    private cache;
    private logger;
    constructor(config?: Partial<EmbeddingServiceConfig>);
    /**
     * Load persisted embeddings from disk into the in-memory cache at startup.
     * Prevents re-generating all embeddings after every Docker restart.
     */
    private loadCacheFromDisk;
    /**
     * Generate embedding for a single text
     */
    generateEmbedding(text: string): Promise<EmbeddingResponse>;
    /**
     * Generate embeddings for multiple texts in batch
     */
    batchEmbeddings(texts: string[], cacheKey?: string): Promise<EmbeddingResponse[]>;
    /**
     * Process a single batch of texts
     */
    private processBatch;
    /**
     * Generate embedding from API (OpenAI or llama.cpp)
     */
    private generateEmbeddingFromAPI;
    /**
      * Generate embeddings from API in batch (OpenAI or llama.cpp)
      */
    private generateEmbeddingsFromAPI;
    /**
     * Generate a deterministic placeholder embedding for testing
     */
    private generatePlaceholderEmbedding;
    /**
      * Save embedding to cache file
      */
    private saveToCacheFile;
    /**
     * Get cache directory path
     */
    getCacheDirectory(): string;
    /**
     * Clear the cache
     */
    clearCache(): void;
    /**
     * Get cache statistics
     */
    getCacheStats(): {
        size: number;
    };
    /**
     * Simple string hash for cache keys
     */
    private hashString;
}
//# sourceMappingURL=EmbeddingService.d.ts.map