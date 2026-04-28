# AI Writing Patterns Catalog

[Back to Humanizer Main Skill](../SKILL.md)

This catalog contains the complete list of 24 AI writing patterns identified in the trailofbits/skills-curated humanizer skill. Each pattern includes signal words, problem description, and before/after examples.

## How to Use This Catalog

When you detect an AI writing pattern in text:

1. Identify which pattern category and specific pattern applies
2. Review the signal words and problem description
3. Use the before/after example as a guide for replacement
4. Apply the natural alternative while preserving original meaning

---

## Category 1: Content Patterns (6 patterns)

These patterns involve overuse of certain concepts, words, or content structures.

### Pattern 1: Inflated Significance

**Signal Words:** testament, landmark, pivotal moment, monumental, historic, groundbreaking, revolutionary, unprecedented, paradigm-shifting, watershed moment

**Problem:** AI tends to overstate the importance of things, using grandiose language that sounds unnatural or insincere.

```ai
This discovery is a testament to years of dedicated research and represents a pivotal moment in the field.
```

```human
This discovery builds on years of research and represents important progress in the field.
```

---

### Pattern 2: Promotional Language

**Signal Words:** vibrant, groundbreaking, revolutionary, exceptional, outstanding, remarkable, extraordinary, unparalleled, unmatched, superior

**Problem:** AI often uses promotional or marketing language that sounds hype-driven rather than informative.

```ai
Our platform offers a vibrant, groundbreaking solution that delivers exceptional results.
```

```human
Our platform solves real problems with practical tools that work consistently.
```

---

### Pattern 3: AI Vocabulary (Generic filler words)

**Signal Words:** additionally, crucially, importantly, significantly, notably, essentially, fundamentally, in conclusion, to summarize, to reiterate

**Problem:** AI overuses these transitional and filler words, often inappropriately or redundantly.

```ai
Additionally, crucially, and importantly, the system must handle errors gracefully.
```

```human
The system must handle errors gracefully—this is critical for reliability.
```

---

### Pattern 4: Vague Attributions

**Signal Words:** experts believe, some say, many people think, it is commonly held, research suggests, studies show, according to some

**Problem:** AI uses vague attributions to sound authoritative without citing specific sources.

```ai
According to some experts, the technique is effective for most cases.
```

```human
The technique works well for most cases (Smith, 2023; Lee, 2024).
```

---

### Pattern 5: Negative Parallelisms

**Signal Words:** not X but Y, not only X but also Y, rather than X, instead of X

**Problem:** Overuse of contrast structures sounds forced and overly formal.

```ai
This approach is not about speed but about accuracy.
```

```human
This approach prioritizes accuracy over speed.
```

---

### Pattern 6: Rule of Three Overuse

**Signal Words:** X, Y, and Z (when forced), three key points, three reasons, three benefits

**Problem:** Forcing three items when a different number would be more natural.

```ai
The three main benefits are performance, reliability, and maintainability.
```

```human
The key benefits are performance, reliability, and maintainability.
```

---

## Category 2: Language Patterns (6 patterns)

These patterns involve specific words, phrases, or linguistic choices that sound AI-generated.

### Pattern 7: Em Dash Overuse

**Signal Words:** — (multiple in same sentence or paragraph)

**Problem:** AI overuses em dashes for dramatic effect, often where simpler punctuation would work better.

```ai
The system — which is designed for reliability — must handle errors — not ignore them — gracefully.
```

```human
The system must handle errors gracefully—it's designed for reliability.
```

---

### Pattern 8: Excessive Conjunctive Phrases

**Signal Words:** and, which, who (repeated chains)

**Problem:** AI creates long, winding sentences with multiple conjunctions that are hard to follow.

```ai
The code, which is written in Python, which is popular for its readability, and which has many libraries, which make development faster, is widely used.
```

```human
The code is written in Python, a language known for readability and fast development through its rich library ecosystem.
```

---

### Pattern 9: Passive Voice Overuse

**Signal Words:** was/were + past participle, it is believed, it is suggested

**Problem:** AI defaults to passive voice, making writing less direct and engaging.

```ai
The results were analyzed and the conclusions were drawn.
```

```human
We analyzed the results and drew conclusions.
```

---

### Pattern 10: Redundant Modifiers

**Signal Words:** very, really, quite, somewhat, pretty (overused)

**Problem:** AI uses modifiers to add emphasis that's unnecessary or weak.

```ai
This is a very important and really crucial consideration.
```

```human
This is a crucial consideration.
```

---

### Pattern 11: Formal Word Choice

**Signal Words:** utilize, demonstrate, indicate, facilitate, implement, commence, terminate, additional, regarding, concerning

**Problem:** AI uses overly formal synonyms when simpler words would work better.

```ai
We will utilize the data to demonstrate the effectiveness of the approach.
```

```human
We'll use the data to show how effective the approach is.
```

---

### Pattern 12: Robotic Transitions

**Signal Words:** in conclusion, to summarize, in summary, to reiterate, as previously mentioned, as noted earlier

**Problem:** AI relies on formulaic transitions that sound like writing templates.

```ai
In conclusion, to summarize, and as previously mentioned, the system is complex.
```

```human
The system is complex, and that complexity affects everything we do.
```

---

## Category 3: Style Patterns (6 patterns)

These patterns involve structural and formatting issues that betray AI authorship.

### Pattern 13: Repetitive Sentence Structure

**Signal Words:** (repeated patterns across sentences)

**Problem:** AI writes sentences with nearly identical structure, creating a monotonous rhythm.

```ai
The system processes data. The system stores results. The system generates reports.
```

```human
The system processes data, stores results, and generates reports.
```

---

### Pattern 14: Overly Long Sentences

**Signal Words:** (sentences over 35 words)

**Problem:** AI creates long, complex sentences that are hard to follow.

```ai
When implementing this feature, developers should consider that it requires careful attention to edge cases, which are often overlooked but can lead to significant issues in production environments, especially when dealing with user input that may not conform to expected formats.
```

```human
This feature needs careful edge case handling. Unhandled edge cases cause production issues, especially with unexpected user input.
```

---

### Pattern 15: Underuse of Contractions

**Signal Words:** (missing contractions where natural)

**Problem:** AI avoids contractions, making writing sound stiff and formal.

```ai
It is important to understand that this approach will not work in all cases.
```

```human
It's important to understand that this approach won't work in all cases.
```

---

### Pattern 16: Formulaic Opening/Closing

**Signal Words:** in today's world, in conclusion, to wrap up, I hope this helps, let me know if you have questions

**Problem:** AI uses canned openings and closings that sound like templates.

```ai
In today's rapidly evolving technological landscape, it is more important than ever to consider these factors. I hope this information helps you in your decision-making process.
```

```human
These factors matter because the tech landscape keeps changing fast. Think about how each option affects your long-term goals.
```

---

### Pattern 17: Overuse of "This" and "That"

**Signal Words:** this, that (repeated without clear antecedents)

**Problem:** AI overuses "this" and "that" without clear reference, creating ambiguity.

```ai
The system has three components. This is important because this affects reliability.
```

```human
The system has three components. The architecture affects reliability—get that wrong and everything suffers.
```

---

### Pattern 18: Mechanical Lists

**Signal Words:** (numbered or bulleted lists in unnatural contexts)

**Problem:** AI uses lists where prose would flow better, or creates lists that feel artificial.

```ai
The key features are:
1. Fast performance
2. Easy to use
3. Reliable operation
```

```human
The system is fast, easy to use, and reliable—three features that make it practical for daily use.
```

---

## Category 4: Communication Patterns (6 patterns)

These patterns involve how ideas are expressed or communicated.

### Pattern 19: Over-Explanation

**Signal Words:** to be clear, to explain, to elaborate, as I mentioned before, in more detail

**Problem:** AI over-explains simple concepts as if the reader can't understand.

```ai
To be clear and to explain in more detail, the function returns a boolean value that indicates whether the operation succeeded.
```

```human
The function returns true if the operation succeeds, false otherwise.
```

---

### Pattern 20: Defending the Obvious

**Signal Words:** it should be clear that, obviously, as you can see, naturally, as expected

**Problem:** AI assumes the reader needs excessive explanation of basic concepts.

```ai
As you can see, obviously, and as should be clear to anyone familiar with the topic...
```

```human
Anyone familiar with the topic knows this works a certain way.
```

---

### Pattern 21: Hedging Language

**Signal Words:** perhaps, maybe, might, could, possibly, potentially, arguably, somewhat, in some cases

**Problem:** AI overuses hedging to avoid committing to statements.

```ai
This approach might potentially improve performance in some cases.
```

```human
This approach improves performance—every test showed a 20-30% gain.
```

---

### Pattern 22: Formulaic Problem-Solution Structure

**Signal Words:** the problem is, the solution is, to address this, we propose, therefore, thus, hence

**Problem:** AI forces rigid problem-solution frameworks that sound academic rather than practical.

```ai
The problem is that the current system is slow. The solution is to implement caching. Therefore, we propose implementing a caching layer.
```

```human
The system is slow—caching would fix it. Let's add a cache layer.
```

---

### Pattern 23: Overuse of "We"

**Signal Words:** we, our, us, our team

**Problem:** AI overuses "we" to create a sense of authority or team effort.

```ai
We believe that our team has developed an approach that we think our users will find valuable.
```

```human
I've developed an approach users find valuable.
```

---

### Pattern 24: Robotic Politeness

**Signal Words:** please, thank you, kindly, appreciate, I would appreciate, grateful

**Problem:** AI uses excessive politeness markers that sound unnatural in technical contexts.

```ai
Please let me know if you would appreciate any additional information. I would be grateful for your feedback.
```

```human
Let me know if you want more details. Feedback is welcome.
```

---

## Quick Reference: Pattern Categories Summary

| Category | Count | Key Indicators |
|---|---|---|
| Content | 6 | Inflated significance, promotional language, vague attributions |
| Language | 6 | Em dashes, long sentences, passive voice, formal words |
| Style | 6 | Repetitive structure, formulaic openings, mechanical lists |
| Communication | 6 | Over-explanation, hedging, robotic politeness |

---

## Tips for Effective Humanization

1. **Read Aloud** — If it sounds odd when spoken, rewrite it
2. **Vary Sentence Length** — Mix short, punchy sentences with longer ones
3. **Use Contractions** — "It's" instead of "It is", "don't" instead of "do not"
4. **Cut Redundancy** — Remove words that don't add meaning
5. **Be Direct** — Say what you mean without padding
6. **Use Active Voice** — "The code runs" instead of "The code is executed"
7. **Know Your Audience** — Adjust tone based on who's reading

---

*For more information about this skill, see the [main humanizer documentation](../SKILL.md).*
