# 30-second demo recording — script

**Goal:** make the abstract concrete in 30 seconds. Viewer should leave thinking *"the agent paid real money to get real nutrition data without a signup."*

**Output:** a silent, looping `.mp4` or `.gif` (≤5 MB). Captions overlaid as on-screen text. No voiceover — viewers watch with sound off in feeds.

## Setup (one-time, before recording)

1. **Use Claude Desktop** (cleaner UI than Claude Code's terminal). MCP config already has `nutriref` wired up via the production install (`nutriref-mcp` command).
2. **Fund the wallet** with ~$1 USDC on Base — enough for plenty of takes.
3. **Browser tab open** to https://basescan.org/address/YOUR_WALLET so you can flash the receipt at the end.
4. **Screen recorder:** OBS (free), ScreenToGif (Windows, free), or QuickTime (Mac). Record at 1080p, then crop. Target 24 fps to keep file size down.
5. **Hide everything** except the Claude window — close notifications, hide taskbar, set OS to Do Not Disturb.

## Beat-by-beat (30 seconds total)

| Time | What's on screen | On-screen caption |
|---|---|---|
| 0:00–0:03 | Claude Desktop, empty conversation. Type the prompt slowly enough to read: **"Is Greek yogurt or cottage cheese better protein-per-calorie? Use NutriRef."** | *(no caption — let the typing speak)* |
| 0:03–0:05 | Hit enter. Claude's thinking indicator appears. | **"Claude has no API key. The agent pays per call."** |
| 0:05–0:12 | Tool call panel expands: `nutrition_search("greek yogurt")` → result → `nutrition_search("cottage cheese")` → result → `nutrition_compare([id1, id2])` → result. Let viewer see the JSON briefly. | **"Three MCP tool calls. $0.005 total in USDC."** |
| 0:12–0:22 | Claude's prose answer appears, summarizing the comparison ("cottage cheese has ~13g protein per 100 cal vs. greek yogurt's ~10g…"). Highlight one or two specific numbers. | **"Real USDA FoodData Central. No API key. No signup."** |
| 0:22–0:27 | Cut to the BaseScan tab. The most recent USDC transfer (a few cents) is at the top. Mouse-hover or briefly zoom on the amount + timestamp. | **"On-chain receipt. Settled in <2 seconds on Base."** |
| 0:27–0:30 | End card. Static frame, hold for 3 seconds. | **"pip install nutriref-mcp · nutriref.xyz"** |

## Cutting tips

- **First 3 seconds matter most.** On Twitter/HN the autoplay frame is t=0; make sure the prompt is partially visible from frame one.
- **Speed up tool-call JSON scroll-through** to 1.5x — JSON is filler, the *fact that tools ran* is the signal.
- **Don't dwell** on the prose answer. People can pause if they want to read.
- **Loop seamlessly:** end card freeze-frame matches a clean cut back to the empty Claude window at t=0.
- **Two versions:** a `.mp4` (HN, blog) and a `.gif` (Twitter inline, README hero).

## Where to use it

- **README hero** — drop above the badges with `![demo](docs/promo/demo.gif)`
- **HN comment** (first reply to your own post — algorithm-friendly)
- **Twitter thread** opener
- **Base/Coinbase devrel cold DM** — leads with the gif, then a paragraph of context
- **MCP Discord #showcase**

## Common mistakes to avoid

- Voiceover. Feeds are muted. Captions only.
- Showing your real wallet address with funds. The agent wallet should hold <$5 — burner-style.
- Boring query ("calories in banana"). It doesn't show off the compare tool, which is the most impressive of the four.
- Recording at 4K. Bloats file, gets recompressed by every platform anyway. 1080p is plenty.
- Long intro. No "Hi I'm Derek" title cards. Start *inside* the prompt.

## Alternate query if the compare-tool answer is boring

"Build me a 600-calorie breakfast with 40g protein from oatmeal, eggs, and greek yogurt. Show the grams." — exercises `nutrition_recipe` and produces a more visually interesting result (a small table).
