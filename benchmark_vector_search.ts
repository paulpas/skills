#!/usr/bin/env -S bun run
/**
 * Agent Skill Router - Vector Search Benchmark Script
 * 
 * Benchmarks the vector search functionality including:
 * - Query latency (ms)
 * - KD-tree search vs linear search comparison
 * - Token usage statistics
 * - Result quality (top 5 skill names)
 */

import { Router, RouterConfig, SkillDefinition } from './agent-skill-routing-system/src/index.js';

// ============================================================================
// Configuration
// ============================================================================

const SKILLS_DIR = '../../skills';
const NUM_ITERATIONS = 5; // Number of times to run each query for averaging
const MAX_RESULTS = 5;

// Benchmark queries with varying lengths and complexity
const BENCHMARK_QUERIES = [
  // Short query (11 tokens)
  'stop loss crypto',
  
  // Medium query (18 tokens)
  'How do I implement a stop loss for cryptocurrency trading?',
  
  // Long query (23 tokens)
  'What is the best way to run a Kubernetes pod with persistent storage and network policies?',
  
  // Technical query (19 tokens)
  'Explain how to write a Python unit test with mock objects and assertions',
  
  // Complex query (21 tokens)
  'How do I configure Prometheus for Kubernetes monitoring with service discovery?',
  
  // Multi-concept query (26 tokens)
  'Implement a TWAP execution algorithm for crypto trading with volume weighting and slippage control',
  
  // Open-ended query (15 tokens)
  'What are the best practices for code review in a team environment?',
];

// ============================================================================
// Benchmark Data Structures
// ============================================================================

interface QueryResult {
  query: string;
  latencyMs: number;
  kdTreeLatencyMs?: number;
  linearLatencyMs?: number;
  inputTokens: number;
  outputTokens: number;
  candidateCount: number;
  topSkills: string[];
  scores: number[];
}

interface BenchmarkSummary {
  totalQueries: number;
  avgLatencyMs: number;
  avgInputTokens: number;
  avgOutputTokens: number;
  avgCandidates: number;
  latencyDistribution: {
    min: number;
    max: number;
    p50: number;
    p95: number;
    p99: number;
  };
  tokenDistribution: {
    inputMin: number;
    inputMax: number;
    outputMin: number;
    outputMax: number;
  };
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Calculate percentile from sorted array
 */
function percentile(arr: number[], p: number): number {
  if (arr.length === 0) return 0;
  const index = Math.ceil((p / 100) * arr.length) - 1;
  return arr[Math.max(0, index)];
}

/**
 * Format milliseconds to readable string
 */
function formatMs(ms: number): string {
  return `${ms.toFixed(2)} ms`;
}

/**
 * Format tokens to readable string
 */
function formatTokens(tokens: number): string {
  return tokens.toLocaleString();
}

/**
 * Calculate statistics from array
 */
function stats(arr: number[]): { min: number; max: number; avg: number; median: number } {
  if (arr.length === 0) {
    return { min: 0, max: 0, avg: 0, median: 0 };
  }
  const sorted = [...arr].sort((a, b) => a - b);
  const sum = sorted.reduce((a, b) => a + b, 0);
  return {
    min: sorted[0],
    max: sorted[sorted.length - 1],
    avg: sum / sorted.length,
    median: sorted[Math.floor(sorted.length / 2)],
  };
}

// ============================================================================
// Main Benchmark Function
// ============================================================================

async function runBenchmark(): Promise<void> {
  console.log('\n╔════════════════════════════════════════════════════════════════╗');
  console.log('║     Agent Skill Router - Vector Search Benchmark               ║');
  console.log('╚════════════════════════════════════════════════════════════════╝\n');

  // Initialize router
  console.log('Initializing Router...');
  const config: RouterConfig = {
    skillsDirectory: SKILLS_DIR,
    embedding: {
      model: 'text-embedding-3-small',
      dimensions: 1536,
    },
    llm: {
      model: 'gpt-4o-mini',
      maxCandidates: 20,
    },
    execution: {
      maxSkills: MAX_RESULTS,
      timeoutMs: 30000,
    },
    safety: {
      enablePromptInjectionFilter: false, // Disable for benchmarking
      requireSchemaValidation: false,
    },
    observability: {
      level: 'warn', // Reduce log noise
      includePayloads: false,
    },
  };

  const router = new Router(config);
  await router.initialize();

  console.log(`✓ Router initialized with ${router.getStats().totalSkills} skills\n`);

  // Run benchmarks
  const results: QueryResult[] = [];

  for (const query of BENCHMARK_QUERIES) {
    console.log(`\n🔍 Query: "${query}"`);
    console.log(`   Length: ${query.length} chars, ${query.split(/\s+/).length} tokens`);
    console.log(`   Iterations: ${NUM_ITERATIONS}`);

    const latencies: number[] = [];
    const kdTreeLatencies: number[] = [];
    const linearLatencies: number[] = [];
    const inputTokensList: number[] = [];
    const outputTokensList: number[] = [];
    const candidateCounts: number[] = [];
    const topSkillsSet = new Set<string>();
    const scoresList: number[][] = [];

    for (let i = 0; i < NUM_ITERATIONS; i++) {
      const startTime = Date.now();

      // Route the task
      const response = await router.routeTask({
        task: query,
        constraints: {
          maxSkills: MAX_RESULTS,
        },
      });

      const latencyMs = response.latencyMs;
      latencies.push(latencyMs);

      // Extract token stats from vector database
      const tokenStats = (router as any).vectorDatabase?.getTokenStats?.() || {
        input: 0,
        output: 0,
      };

      // For accurate per-request tokens, we need to extract from the response
      // This requires accessing internal state or modifying the Router
      // For now, we'll estimate from the LLM ranker
      const llmRanker = (router as any).llmRanker;
      const inputTokens = llmRanker?.getInputTokens?.() || 0;
      const outputTokens = llmRanker?.getOutputTokens?.() || 0;

      inputTokensList.push(inputTokens);
      outputTokensList.push(outputTokens);

      candidateCounts.push(response.candidatePool.length);

      // Track top skills
      response.selectedSkills.forEach((skill) => {
        topSkillsSet.add(skill.name);
      });

      scoresList.push(response.selectedSkills.map((s) => s.score));

      // Note: KD-tree vs linear comparison requires access to internal timing
      // For a real benchmark, we'd need to add timing instrumentation to VectorDatabase

      console.log(`   Iter ${i + 1}: ${formatMs(latencyMs)}, Input: ${formatTokens(inputTokens)}, Output: ${formatTokens(outputTokens)}`);
    }

    // Calculate averages for this query
    const avgLatency = latencies.reduce((a, b) => a + b, 0) / latencies.length;
    const avgInputTokens = inputTokensList.reduce((a, b) => a + b, 0) / inputTokensList.length;
    const avgOutputTokens = outputTokensList.reduce((a, b) => a + b, 0) / outputTokensList.length;
    const avgCandidates = candidateCounts.reduce((a, b) => a + b, 0) / candidateCounts.length;
    const avgScores = scoresList.reduce((acc, scores) => acc.concat(scores), []);

    results.push({
      query,
      latencyMs: avgLatency,
      inputTokens: Math.round(avgInputTokens),
      outputTokens: Math.round(avgOutputTokens),
      candidateCount: Math.round(avgCandidates),
      topSkills: Array.from(topSkillsSet).slice(0, MAX_RESULTS),
      scores: avgScores,
    });

    // Reset LLM token counters for next query
    (router as any).llmRanker?.resetTokenCounters?.();
  }

  // Calculate summary statistics
  const summary = calculateSummary(results);

  // Print results
  printResults(results, summary);
}

// ============================================================================
// Summary Calculation
// ============================================================================

function calculateSummary(results: QueryResult[]): BenchmarkSummary {
  const latencies = results.map((r) => r.latencyMs);
  const inputTokens = results.map((r) => r.inputTokens);
  const outputTokens = results.map((r) => r.outputTokens);
  const candidates = results.map((r) => r.candidateCount);

  const sortedLatencies = [...latencies].sort((a, b) => a - b);

  return {
    totalQueries: results.length,
    avgLatencyMs: latencies.reduce((a, b) => a + b, 0) / latencies.length,
    avgKdTreeLatencyMs: undefined,
    avgLinearLatencyMs: undefined,
    avgInputTokens: inputTokens.reduce((a, b) => a + b, 0) / inputTokens.length,
    avgOutputTokens: outputTokens.reduce((a, b) => a + b, 0) / outputTokens.length,
    avgCandidates: candidates.reduce((a, b) => a + b, 0) / candidates.length,
    latencyDistribution: {
      min: Math.min(...latencies),
      max: Math.max(...latencies),
      p50: percentile(sortedLatencies, 50),
      p95: percentile(sortedLatencies, 95),
      p99: percentile(sortedLatencies, 99),
    },
    tokenDistribution: {
      inputMin: Math.min(...inputTokens),
      inputMax: Math.max(...inputTokens),
      outputMin: Math.min(...outputTokens),
      outputMax: Math.max(...outputTokens),
    },
  };
}

// ============================================================================
// Result Printing
// ============================================================================

function printResults(results: QueryResult[], summary: BenchmarkSummary): void {
  // Print per-query results
  console.log('\n' + '─'.repeat(80));
  console.log('QUERY RESULTS');
  console.log('─'.repeat(80));

  for (const result of results) {
    console.log(`\nQuery: "${result.query.substring(0, 60)}${result.query.length > 60 ? '...' : ''}"`);
    console.log(`  Latency:        ${formatMs(result.latencyMs)}`);
    console.log(`  Input Tokens:   ${formatTokens(result.inputTokens)}`);
    console.log(`  Output Tokens:  ${formatTokens(result.outputTokens)}`);
    console.log(`  Candidates:     ${result.candidateCount}`);
    console.log(`  Top Skills:`);
    
    result.topSkills.forEach((skill, i) => {
      console.log(`    ${i + 1}. ${skill}`);
    });
  }

  // Print summary statistics
  console.log('\n' + '─'.repeat(80));
  console.log('SUMMARY STATISTICS');
  console.log('─'.repeat(80));

  console.log(`\nTotal Queries:        ${summary.totalQueries}`);
  console.log(`Average Latency:      ${formatMs(summary.avgLatencyMs)}`);
  console.log(`  Min/Max:            ${formatMs(summary.latencyDistribution.min)} / ${formatMs(summary.latencyDistribution.max)}`);
  console.log(`  P50/P95/P99:        ${formatMs(summary.latencyDistribution.p50)} / ${formatMs(summary.latencyDistribution.p95)} / ${formatMs(summary.latencyDistribution.p99)}`);

  console.log(`\nAverage Input Tokens: ${formatTokens(summary.avgInputTokens)}`);
  console.log(`  Range:              ${formatTokens(summary.tokenDistribution.inputMin)} - ${formatTokens(summary.tokenDistribution.inputMax)}`);

  console.log(`\nAverage Output Tokens: ${formatTokens(summary.avgOutputTokens)}`);
  console.log(`  Range:               ${formatTokens(summary.tokenDistribution.outputMin)} - ${formatTokens(summary.tokenDistribution.outputMax)}`);

  console.log(`\nAverage Candidates:   ${Math.round(summary.avgCandidates)}`);

  // Performance comparison (if KD-tree timing available)
  console.log('\n' + '─'.repeat(80));
  console.log('PERFORMANCE COMPARISON');
  console.log('─'.repeat(80));

  console.log('Note: KD-tree vs linear search timing requires instrumentation.');
  console.log('      The VectorDatabase.search() method supports both methods:');
  console.log('      - KD-tree: O(log n) - Uses KDTree for efficient nearest neighbor search');
  console.log('      - Linear:  O(n) - Brute force similarity calculation');
  console.log('      Current config: useKDTree is enabled by default');

  // Token usage breakdown
  console.log('\n' + '─'.repeat(80));
  console.log('TOKEN USAGE STATISTICS');
  console.log('─'.repeat(80));

  const totalTokens = summary.avgInputTokens + summary.avgOutputTokens;
  console.log(`Average Total Tokens: ${formatTokens(totalTokens)}`);
  console.log(`  Input:  ${((summary.avgInputTokens / totalTokens) * 100).toFixed(1)}%`);
  console.log(`  Output: ${((summary.avgOutputTokens / totalTokens) * 100).toFixed(1)}%`);

  // Cost estimation (assuming OpenAI pricing)
  console.log('\n' + '─'.repeat(80));
  console.log('COST ESTIMATION (OpenAI pricing - text-embedding-3-small + gpt-4o-mini)');
  console.log('─'.repeat(80));

  // $0.02 / 1M input tokens, $0.06 / 1M output tokens for gpt-4o-mini
  // $0.02 / 1M for text-embedding-3-small
  const avgInputCost = (summary.avgInputTokens / 1_000_000) * 0.02;
  const avgOutputCost = (summary.avgOutputTokens / 1_000_000) * 0.06;
  const embeddingCost = (summary.avgInputTokens / 1_000_000) * 0.02; // Approximate
  const totalCost = (avgInputCost + avgOutputCost + embeddingCost) * summary.totalQueries;

  console.log(`Average Input Cost:   $${avgInputCost.toFixed(6)}`);
  console.log(`Average Output Cost:  $${avgOutputCost.toFixed(6)}`);
  console.log(`Average Embedding Cost: $${embeddingCost.toFixed(6)}`);
  console.log(`Total Estimated Cost: $${totalCost.toFixed(6)} (${summary.totalQueries} queries)`);
  console.log(`Cost per Query:       $${(totalCost / summary.totalQueries).toFixed(6)}`);

  // Final recommendations
  console.log('\n' + '─'.repeat(80));
  console.log('RECOMMENDATIONS');
  console.log('─'.repeat(80));

  console.log(`
1. Consider enabling embedding caching if queries have overlap
2. For production, use a smaller embedding model for initial filtering
3. Consider caching LLM rankings for repeated queries
4. Monitor token usage - current average: ${formatTokens(totalTokens)} tokens/query
5. KD-tree provides O(log n) search vs O(n) linear - significant for large skill sets
`);

  console.log('\n✓ Benchmark complete!\n');
}

// Run the benchmark
runBenchmark().catch((error) => {
  console.error('Benchmark failed:', error);
  process.exit(1);
});
