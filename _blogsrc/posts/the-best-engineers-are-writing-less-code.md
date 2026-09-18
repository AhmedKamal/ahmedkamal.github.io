---
title: "The best engineers are writing less code"
date: "2026-09-17"
slug: "the-best-engineers-are-writing-less-code"
description: "Most of the room used AI coding tools every day. Nobody trusted the output enough to ship it. That gap is a process problem, and it closes when you change what you think you are writing."
archived: false
image: "https://ahmedkamal.me/og/best-engineers-card-2.png"
---

I asked a room of engineers two questions.

First: who uses AI coding tools every day? Most of the hands went up.

Second: who trusts the output enough to ship it without reviewing? Not a single hand.

That was in April, at [Tamara's Sandbox](https://youtu.be/kJXikdw8rl8). The same gap shows up in the industry numbers: around 92% of American developers report using AI tools daily, and about 3% report high trust in what comes back. Adoption is nearly total. Trust is still not there.

I think that gap is the most interesting thing happening in software right now. I also think it is not a model problem. It is a process problem, and it closes when you change your mind about what you are actually writing.

## Twelve months against twelve years

I have been building data and ML systems for about thirteen years, witnessing how products get built at Careem, Uber, Stream, and now at Hudhud. In the last year, the way my org works changed more than in the twelve years before it.

That is a strong claim, so let me be precise about what changed. It is not that we type less. It is that the artifact we care about moved.

## Why vibe coding broke

For a while last year the story was that you could describe an app and receive an app. For a to-do list, that worked. For anything real, it fell apart, and it fell apart in a way worth understanding.

Here is the analogy I keep coming back to. Vibe coding is like compiling C++ down to assembly, deleting the C++, and then trying to maintain the assembly. Everything you needed in order to change the system safely was in the thing you threw away.

Three failures followed from that, and I saw all three.

**Context evaporated.** You would open a chat, work through a problem, make a dozen decisions, and close the tab. Think about how absurd that is. When humans have a design discussion at a whiteboard, we do not admire it and then wipe the board. We turn it into a design document or an RFC, because that is the contract everyone aligned on. With AI we were wiping the board every single time.

**Decisions got delegated that should never have been.** Which database. Batch or streaming. Which interface boundaries. The model made those calls confidently, without enough understanding of the business to make them well.

**There was no structure to catch any of it.** No specs, no tests, no review gates. Just chat text.

So the industry's conclusion, that vibe coding is a bad idea, is correct. The conclusion many people drew next, that the whole thing is hype, is not.

## The spec is the source code

The reframe that made everything click for me came out of a conversation after the talk, and it is this: the spec is the source code now, and the programming language is the compiled output.

We have done this before. We wrote assembly, then C, then Java, then Python. At each step we handed more decisions to a compiler and stopped reading its output. You do not review the bytecode your Java compiler produces. You do not read the assembly emitted for Android and again for iOS. You write the source carefully, you test the artifact, and you trust the translation.

English is now becoming the source layer. The RFC, the spec, the success criteria, the constraints you set: that is the code you are writing. The Python that comes out the other side is the build artifact.

Once you accept that, a lot of confusing advice resolves itself:

- Context must be versioned, because you version source, not build output.
- Reviewing every generated line is like reading disassembly. Sometimes it is the right call. Usually it means you have not written enough source.
- Writing a better prompt is not the skill. Writing a better spec is.

## Coding the process

What replaces prompting is a process you encode once and reuse.

The shape is the same across the frameworks that have emerged from Google, Amazon, GitHub and others, which tells you something. You write an RFC and you sign it off yourself. You break it into tasks. Independent tasks go to separate agents working in parallel, each in its own branch, each opening a pull request. The rules you would apply to a human contributor apply here: tests pass, linters pass, review gates hold, or the work does not merge.

You are no longer writing the code. You are coding the process by which code gets written.

Some of those frameworks enforce a multi-model review step that is worth calling out, because it maps onto something data people already know. Ensembles beat single models. One model is weak where another is strong. Having a second and third model review every phase is the same instinct as asking two or three colleagues to review something critical, and it costs almost nothing.

## What it looked like in practice

Earlier this year I spent a weekend building an internal tool at Hudhud: a catalog for satellite imagery, with a CLI, connections to Trino and Iceberg, tile stitching, and a set of integration tests.

It came to roughly twenty thousand lines. I wrote almost none of them.

That number is not the point, and I want to be careful here, because it is exactly the kind of number that gets quoted as a boast. The point is where my time went. I spent it on the plan and on the validation criteria. Then, once the first version existed, I spent it doing the thing an architect does when reviewing work from a capable team: hunting for corner cases, pulling on things that looked wrong, deciding what to do about them.

Two moments from that weekend are the whole argument.

**The projection bug.** The system pulled satellite tiles from two different sources, and the agent assumed they shared a projection. They did not. I did not catch that by reading the code. I caught it by looking at the output and seeing that it was wrong. When I pushed back, the model explained why it was fine. I told it that if it were fine, other things would be true that plainly were not. It agreed, and we iterated to a real fix.

**The storage decision.** We use Alibaba Cloud rather than AWS. I wanted integration tests, and there was no good local emulator for OSS, their object store. I knew OSS implements the same interface as S3, so testing against that was sufficient. That is not a hard decision. It is just one that requires knowing our stack, our constraints, and what "sufficient" means for us. No agent had any way to make it.

Both were decisions, not code. That is the pattern. Intervene at decision points, not inside the build.

## The honest counterpoints

If I only told you the good half, I would be doing the thing I dislike about most writing on this subject.

**It can make you slower.** A controlled study by METR in mid-2025 found experienced open-source developers were about 19% slower using AI tools, while believing they were around 20% faster. Feeling fast and being fast are different measurements. A follow-up with 2026 tooling found roughly 18% faster, so the trend is real, but the first result should keep you cautious.

The detail I find most telling is that a large share of the original participants would not join the second study. Their reason was that they no longer wanted to work without AI at all. That is not a productivity measurement. It is a preference that indicates a strong habit, and it is worth noticing.

**Review does not scale.** You can generate a hundred times more code. You still have one brain. Nobody meaningfully reviews twenty thousand lines. If you are not going to read it, then your specs, your tests and your gates have to be good enough to carry the weight instead. If they are not, you are not saving time. You are deferring it.

**The cognitive debt is real, and it surprised me.** In a normal day, the work has natural rest in it. You open a PR, you wait for CI, you get a coffee. In this mode, the easy work is gone and every hour is the hardest part of the job: judgment, debugging, decisions. Eight hours of that is not the same as eight hours of the old thing. I broke my own sleep that weekend, partly from excitement, and I do not think that is a model to hold up.

**And it depends entirely on what you are building.** An internal tool with an owner sitting next to it is one risk profile. A banking system is another. If you are in a regulated business, nobody is going to let you ship unreviewed generated code, and they are right.

## You are still the owner

I lead a team of about sixty people, and there is one rule I repeat when using AI gets discussed. If there is a problem with something you shipped, you own it. Not the AI.

This applies to code, and it applies just as much to the report you generated, or the summary you did not read before forwarding. The tool does not absorb accountability. Nobody has ever blamed a compiler.

So the choice is not whether to trust the system. It is where you put your attention, given that you are accountable either way. If you do not trust it, review it. If you want to review less, then invest in the specs, the criteria and the gates until you have earned the right to. What you cannot do is skip both and hope.

## What this means for building here

The reason I care about this beyond my own team is regional.

For the last twenty or thirty years, the binding constraint on building serious technology in this part of the world has been people. Not ideas, not problems worth solving, not capital in recent years. Engineers. Anyone who has tried to staff an ambitious project here knows the feeling of a plan that is correct and unbuildable.

If the cost of turning a good design into working software drops as much as it appears to be dropping, that constraint loosens. That matters more here than it does in places that never had it.

But it only pays out if you bring something to the process. The differentiator is what does not automate: domain knowledge, architectural judgment, taste, and actually understanding the problem. None of that is a smaller ask than before. It is a larger one. Being an architect is a promotion, and promotions come with harder work, not less of it.

Which is why I would put it this way. Lead the AI. Do not let the AI lead you.
