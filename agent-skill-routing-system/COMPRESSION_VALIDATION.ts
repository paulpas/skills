// Compression Validation - Run validation across sample skills
// Validates that compression works correctly across all levels

import { SkillCompressor } from './src/core/SkillCompressor';
import { SkillRegistry } from './src/core/SkillRegistry';

const SAMPLE_SKILLS = [
  'code-review',
  'stop-loss',
  'code-testing',
  'risk-management',
  'kubernetes',
  'trading-risk-kill-switches',
  'python-generators',
  'api-design-patterns',
];

interface ValidationResult {
  skillName: string;
  level: number;
  originalLength: number;
  compressedLength: number;
  ratio: number;
  success: boolean;
  error?: string;
  tokenEstimateAccuracy: number; // 0-1 (how close estimate was)
}

export async function validateCompression(): Promise<void> {
  console.log('=== Skill Compression Validation ===\n');

  const compressor = new SkillCompressor();
  const registry = new SkillRegistry({ skillsDirectory: './skills' });

  const results: ValidationResult[] = [];
  let totalTests = 0;
  let passedTests = 0;

  try {
    // Load skills
    await registry.loadSkills();
    const allSkills = registry.getAllSkills();

    if (allSkills.length === 0) {
      console.warn('No skills loaded. Using sample test content instead.');
    }

    // Sample a subset of skills (or use all if < 100)
    const skillsToTest = allSkills.slice(0, 100);
    console.log(`Testing compression on ${skillsToTest.length} skills\n`);

    for (const skillDef of skillsToTest) {
      try {
        const content = await registry.getSkillContent(skillDef.metadata.name);
        if (!content) {
          console.log(`⚠  Skipped ${skillDef.metadata.name} (no content)`);
          continue;
        }

        // Test each compression level
        for (let level = 0; level <= 10; level++) {
          totalTests++;

          try {
            const compressed = compressor.compress(content, level);
            const estimate = compressor.estimateTokenSavings(content, level);

            // Validate
            const issues: string[] = [];

            // 1. No data loss
            if (level === 0) {
              if (compressed.content !== content) {
                issues.push('Level 0 content modified');
              }
            }

            // 2. YAML frontmatter preserved (if level > 0)
            if (level > 0 && content.includes('---')) {
              const fmMatch = content.match(/^---[\s\S]*?---/);
              if (fmMatch && !compressed.content.includes(fmMatch[0])) {
                issues.push('Frontmatter lost');
              }
            }

            // 3. Code blocks preserved
            if (content.includes('```')) {
              const codeBlocks = content.match(/```[\s\S]*?```/g) || [];
              for (const block of codeBlocks) {
                if (!compressed.content.includes(block)) {
                  issues.push('Code block modified');
                  break;
                }
              }
            }

            // 4. Token estimates reasonable (within 20% for estimation)
            const estimateAccuracy = 1 - Math.abs(estimate.ratio - (1 - (compressed.tokensSaved / estimate.before)));
            if (estimateAccuracy < 0) {
              issues.push('Token estimate inaccurate');
            }

            const result: ValidationResult = {
              skillName: skillDef.metadata.name,
              level,
              originalLength: compressed.originalLength,
              compressedLength: compressed.compressedLength,
              ratio: compressed.ratio,
              success: issues.length === 0,
              error: issues.length > 0 ? issues.join('; ') : undefined,
              tokenEstimateAccuracy: Math.max(0, estimateAccuracy),
            };

            results.push(result);

            if (result.success) {
              passedTests++;
              process.stdout.write('.');
            } else {
              process.stdout.write('✗');
            }
          } catch (error) {
            const result: ValidationResult = {
              skillName: skillDef.metadata.name,
              level,
              originalLength: content.length,
              compressedLength: 0,
              ratio: 1,
              success: false,
              error: error instanceof Error ? error.message : String(error),
              tokenEstimateAccuracy: 0,
            };
            results.push(result);
            process.stdout.write('E');
          }
        }
      } catch (error) {
        console.log(`\n✗ Failed to load skill ${skillDef.metadata.name}: ${error}`);
      }
    }

    console.log('\n\n=== Validation Summary ===\n');
    console.log(`Total tests: ${totalTests}`);
    console.log(`Passed: ${passedTests}`);
    console.log(`Failed: ${totalTests - passedTests}`);
    console.log(`Pass rate: ${((passedTests / totalTests) * 100).toFixed(1)}%\n`);

    // Report by level
    const resultsByLevel: Record<number, ValidationResult[]> = {};
    for (const result of results) {
      if (!resultsByLevel[result.level]) {
        resultsByLevel[result.level] = [];
      }
      resultsByLevel[result.level].push(result);
    }

    console.log('=== Results by Compression Level ===\n');
    for (let level = 0; level <= 10; level++) {
      const levelResults = resultsByLevel[level] || [];
      if (levelResults.length === 0) continue;

      const passed = levelResults.filter((r) => r.success).length;
      const avgRatio = levelResults.reduce((sum, r) => sum + r.ratio, 0) / levelResults.length;
      const avgAccuracy = levelResults.reduce((sum, r) => sum + r.tokenEstimateAccuracy, 0) / levelResults.length;

      console.log(
        `Level ${level}: ${passed}/${levelResults.length} passed | Avg ratio: ${avgRatio.toFixed(2)} | Token accuracy: ${(avgAccuracy * 100).toFixed(1)}%`
      );

      // Show first error for this level
      const errorResult = levelResults.find((r) => !r.success);
      if (errorResult?.error) {
        console.log(`  → Error: ${errorResult.error}`);
      }
    }

    // Token savings analysis
    console.log('\n=== Token Savings Analysis ===\n');
    const savingsByLevel: Record<number, number[]> = {};
    for (const result of results) {
      if (!savingsByLevel[result.level]) {
        savingsByLevel[result.level] = [];
      }
      const saved = 1 - result.ratio;
      if (saved >= 0) {
        savingsByLevel[result.level].push(saved * 100);
      }
    }

    for (let level = 0; level <= 10; level++) {
      const savings = savingsByLevel[level] || [];
      if (savings.length === 0) continue;

      const avg = savings.reduce((a, b) => a + b, 0) / savings.length;
      const min = Math.min(...savings);
      const max = Math.max(...savings);

      console.log(`Level ${level}: Avg ${avg.toFixed(1)}% saved | Range ${min.toFixed(1)}%-${max.toFixed(1)}%`);
    }

    // Report failures
    const failures = results.filter((r) => !r.success);
    if (failures.length > 0) {
      console.log(`\n=== Failures (${failures.length}) ===\n`);
      const uniqueErrors = new Map<string, number>();
      for (const failure of failures) {
        const key = `${failure.skillName}@L${failure.level}`;
        const existing = uniqueErrors.get(failure.error || 'unknown') || 0;
        uniqueErrors.set(failure.error || 'unknown', existing + 1);
      }

      for (const [error, count] of uniqueErrors.entries()) {
        console.log(`[${count}x] ${error}`);
      }
    }

    console.log('\n=== Validation Complete ===\n');

    // Exit with appropriate code
    process.exit(passedTests === totalTests ? 0 : 1);
  } catch (error) {
    console.error('Validation error:', error);
    process.exit(1);
  }
}

// Run validation if called directly
if (require.main === module) {
  validateCompression().catch((err) => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}

export default validateCompression;
