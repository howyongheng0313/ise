# Santa Tell Me
### *are you really there...*

> A 1950s analog horror / Creepy-Rules Fiction experience  
> Disguised as a basic Pygame Christmas student project.  
> The pixel game is completely untouched. The horror lives entirely in the narrative wrappers.

---

## CONCEPT

**Santa Tell Me** is a psychological horror visual novel wrapped around a generic pixel game ("Santa Adventure"). The pixel game — Level 1 (Frosty Forest Run) and Level 2 (Present Delivery Maze) — is submitted exactly as originally written by the development team. It is intentionally basic. The contrast between the cheerful 8-bit pixel game and the deeply unsettling 1950s analog horror narrative framework is the design.

**Era & Setting:** American 1950s Christmas / Cold War suburbia. Globally iconic, deliberately uncanny. The era of performative happiness, nuclear family perfection, and anxieties hidden beneath tinsel. Pixel art reads as CRT television static from this era — a feature, not a flaw.

**The Narrator:** A Hollow Santa. Warm. Grandfatherly. Genuinely jolly. He was the first one trapped in the loop. He has run it so many times that the warmth detached entirely from meaning. He collects souls the way he used to collect wish lists — with care, with delight, with zero malice. He thinks this is helping. That is the horror. He calls the player "child." He applauds good answers. He expresses polite disappointment at failure. He is never angry, never loud. He is a curator.

---

## THE SIX RULES
*(Encoded in the Opening Prophecy. Never explained directly.)*

| # | Rule | How It Manifests |
|---|------|-----------------|
| 1 | **Use your eye — but don't trust it.** | Keyword answers appear **bolded and coloured** (dark maroon) in dialogue. Players see them. Players don't notice them. |
| 2 | **Don't trust your instinct.** | The Sphinx UI triggers automatic Christmas associations (SANTA, ANGEL, CAROL, FEAST). All are wrong. The real answers are the dark keywords you locked in. |
| 3 | **Kids should have a good memory.** | The keyword seen in Loop 1's breakfast scene is the same across all reincarnations. Players who remember, pass. Players who don't, learn what forgetting costs. |
| 4 | **Four is the universe's favourite number.** | Every personal math question must be answered with 4. No exceptions. No matter what is asked. |
| 5 | **A human has 5 parts (4 + soul).** | Each successful escape from the pixel world costs one physical part as a toll. After 4 loops, only the soul remains. The MC is erased from the family photo. |
| 6 | **Valour tastes sweetest. Wit is a test.** | Dying in the pixel game = brave death = tasty soul = eaten instantly (True Game Over). Passing the pixel game = witty = Sphinx quiz. Failing the quiz means you are a pure/dumb soul, and are thrown back into the pixel game (Reincarnation). Passing the quiz means you escape, but leave a part of yourself behind. |

---

## OPENING PROPHECY
*(Displays before the eye-opening effect. Courier font, dark background, fades in and out.)*

```text
Mind the colors, bold and bright,
But do not trust your given sight.
The first thought in your little head,
Is just a trap where fools are led.

A proper child will memorize,
The secrets hidden in plain eyes.
And when the universe keeps score,
The only answer here is Four.

Five candles on a birthday cake —
Blow one out and count what's left to take.
The brave are sweet and quickly chewed,
While witty souls are bitter food.
```

---

## FULL NARRATIVE FLOW

### Phase 0 — Cover Page / Menu
- Title card: **"Santa Tell Me"** (large, faded 1950s serif, muted vintage yellow)
- Subtitle: ***are you really there...*** (small, lowercase, off-centre, typewriter/handwriting font)
- Audio: Music-box cover of *Santa Tell Me* — occasionally skips a note.
- **BGM Mute Toggle:** If player mutes the BGM, a surveillance-style popup appears:
  > *"That's why I said this isn't for the weak-hearted."* > *"But we will let you proceed... in silence."* > Disapproving. Lets them continue anyway. 4 seconds, then moves on.
- **Ominous navigation instructions** (written as warnings):
  > *"Use arrow keys to run. Do not look away."* > *"[Press ENTER to step inside]"*
- **Name Input:** `"Hi. What is your name?"` (default: child)
- **Age Input:** `"Hello, [name]. How old are you turning today?"` — this age is stored and used by Mom in the kitchen scene, AND becomes the trap for the personal math questions later (player will instinctively type their real age, but the correct answer is always 4).

---

### Phase 1 — 1950s Kitchen (Interactive Visual Novel)
**Setting:** MC's POV. Blurry blink — eyes opening. A 1950s kitchen, Christmas morning, supposedly also the MC's birthday. Mom holds a cake. Dad reads the newspaper. Their smiles are slightly too wide. Eyes slightly too open. 

**Note:** On Loop 2, 3, 4 — the prophecy is SKIPPED. The eye-opening begins immediately.

#### The 4 Branching Choices → 4 Keywords
**Mom:** *"Happy birthday, sweetheart! Look at you, already [age] years old. I made your favourite. Go on, take a bite."*

**Branch 1 — Good Child Route:**
Mom's smile widens unnaturally. Dad lowers newspaper, stares without blinking.
> *"You're awfully quiet today, kiddo."*
- *"I heard a noise outside."*
  → Dad: *"Just the winter wind. It can be **cruel** to those who wander off. Best stay inside with us."*
  → **LOCKS KEYWORD: CRUEL**
- *"Why are you staring at me?"*
  → Dad (voice drops): *"Now, don't let your **anger** ruin this wonderful morning. We are a happy family."*
  → **LOCKS KEYWORD: ANGER**

**Branch 2 — Rebellious Child Route:**
Mom's smile doesn't change. Voice goes flat.
> *"We don't waste food in this house."*
- *"The cake looks... cold."*
  → Mom: *"Don't be ungrateful. If it tastes a little bitter, darling, it's just the **frost**."*
  → **LOCKS KEYWORD: FROST**
- `[Try to leave the table]`
  → Mom's hand slams on table: *"Sit down. Stay away from the fireplace, you'll get your new clothes all **sooty**."*
  → **LOCKS KEYWORD: SOOTY**

#### Viewfinder Transition
Dad slides a chunky, red, plastic 1950s View-Master toy across the table.
**[UI Prompt: Look Inside]**
A Dual-Lens effect zooms in (two black circles shrinking to the center), swallowing the screen into claustrophobic pitch black before snapping to the 8-bit Level 1 pixel game.

---

### Phase 2 — Pixel Game (UNTOUCHED)
`level1.py` → `level2.py`. Exactly as written. No modifications. No handicaps.
The pixel game is a cheerful student project. The jarring contrast between the horror framework and the basic pixel game IS the aesthetic.

---

### Phase 3 — The Hijack (Valour vs. Wit)

#### PATH A: VALOUR ROUTE (Died in pixel game)
1. Generic `GAME OVER` screen appears first (drops the player's guard).
2. Holds for 2.5 seconds. No buttons to click.
3. **Hijack triggers:** Screen tears with CRT static. Full-window blood splash (red blend overlay). BGM cuts to dead silence.
4. Narrator (text, slowly): *"Such a brave little soul. You fought well."*
5. Pause. Then: *"Valour tastes... so sweet."*
6. **TRUE GAME OVER.** The player's soul is eaten. They bypass the riddle and the photo entirely. They are kicked directly back to the Main Menu. Their run is dead.

#### PATH B: WIT ROUTE (Passed pixel game — reached Christmas tree)
1. Generic `VICTORY! Merry Christmas!` screen appears first.
2. Holds for 2.5 seconds. No buttons to click.
3. **Hijack triggers:** UI visually melts (glitch effect). Score numbers spin wildly — all land on 4. Screen cuts to black.
4. Narrator: *"You escaped... how cunning. Let us test that wit."*
5. → Riddle Session begins.

---

### Phase 4 — Riddle Session (Sphinx Mechanic)

**UI:** 1950s chalkboard aesthetic. Dark green background. Wooden frame border. Courier font for letter patterns.
**Structure: 3 questions total. 1 attempt each. No going back.**

#### Question 1 — The Instinct Trap (Keyword Quiz)
Chalkboard shows the letter pattern for the player's locked keyword.

| Keyword | UI Pattern | Instinct Trap | Sphinx Question Options (Randomized) |
|---------|------------|---------------|--------------------------------------|
| CRUEL   | `C _ _ _ L`| CAROL         | "A sweet song sung by a choir in the winter wind..." OR "How does the world treat a child who refuses to listen...?" |
| ANGER   | `A N _ E _`| ANGEL         | "It sits at the very top of the tree, watching over the family..." OR "What is the one thing your father told you would ruin this morning?" |
| FROST   | `F _ _ S T`| FEAST / FIRST | "A table full of sweet treats and hot food, gathered around..." OR "What crawls across the bedroom window to trap the warmth inside...?" |
| SOOTY   | `S _ _ T _`| SANTA         | "He comes down the chimney in the dead of night to visit good children..." OR "What is the true color of a burning memory once the warm fire dies?" |

#### Questions 2 & 3 — The Number 4 (Personal Math)
**The answer is ALWAYS 4. No matter what is asked.**
- *"If Santa has nine reindeer but only four to pull your sled to the grave, how many are left in the cold?"*
- *"Four lit candles on a birthday cake. Four heavy walls in a quiet room. How many days until you stop screaming?"*
- *"A human has five parts. If you give your eyes, your voice, your memory, and your form to the man in red... how many parts are left for your soul?"*
- *"Mom, Dad, and You sitting at the table. If a jolly old visitor slides down the chimney to join you, how many plates do we need?"*
- *"Count the corners of a gift box. Now subtract the number of parents who actually love you. What is the final sum?"*
- *"On a scale of one to four, how happy are you to belong to us forever?"*

#### The Result (Escape vs. Reincarnation)
- **FAIL THE QUIZ (The Reincarnation Loop):**
  - If any of the 3 questions are wrong, the quiz is failed.
  - Narrator: *"How delightfully pure and dull. I will throw you back... amuse me in the snow."*
  - The narrator thinks you are a pure, dumb soul. He wants to watch you die.
  - Player is thrown into the `reincarnation_bg.png` transition screen. Loop count increases by 1. Player is forced back to Level 1 to suffer again.

- **PASS THE QUIZ (The Escape):**
  - If all 3 questions are correct, the quiz is passed.
  - Narrator: *"Your cunning appals me. But I will keep a token... since I am stuck here."*
  - You escape the pixel world! But the narrator takes a body part as a toll.
  - Player is sent to the Ending Vignette, then kicked back to the Main Menu.

---

### Phase 5 — Ending Vignettes (The Cost)
After successfully passing a Wit Route riddle session, the **结算画面 (tally screen)** appears. A degrading 1950s family portrait is displayed.

#### 1st Escape — Loss of Sight
**Photo (`family_loop1.png`):** MC standing between Mom and Dad. MC's eyes have been violently scribbled out with thick red ballpoint pen marks.
> *The living room was so bright when I pulled the toy away from my face... I told him the snow glare from the window was just playing tricks on me. I told myself that. I will tell myself that tomorrow, too.*

#### 2nd Escape — Loss of Voice
**Photo (`family_loop2.png`):** Eyes still red scratches. Lower half of MC's face is a smooth, fleshy blur. No mouth.
> *"Are you going to eat your cake, sweetheart?" Mom's smile was still pinned to her cheeks. I opened my mouth to tell her I wasn't hungry... I screamed that I was sorry, over and over. They just kept staring at me, waiting for a sound.*

#### 3rd Escape — Loss of Memory
**Photo (`family_loop3.png`):** MC's entire face and torso washed out, as if a chemical stain dissolved only their figure from the photograph.
> *There was a toy. It was red, I think. Plastic... I know there were rules. Four of them? No, four is just a number. It's my birthday, but I don't know how old I am. The old man in the red suit was laughing in the dark... I can't remember my name.*

#### Loop 4 — Loss of Form (True Ending)
If a player survives and passes the pixel game for a 4th time, there is **NO QUIZ**. The Narrator is moved by their stubborn determination. He lets the soul go, but keeps the physical vessel entirely.
**Photo (`family_loop_final.png`):** Mom and Dad smiling warmly at completely empty space between them. MC is entirely absent.
> *The house is very quiet now. Mom and Dad are smiling at the photograph. There is a gap where someone used to stand. They do not seem to notice. ...at what cost?*

After the True Ending vignette: game closes itself back to the Main Menu. The broadcast ends.

---

## KEYWORD MEMORY RULE *(Cross-loop)*
The locked keyword is determined by the player's breakfast choices in Loop 1. It **persists across all reincarnations** — the same keyword, the same breakfast path. The keyword question pool randomises which of the 2 questions is shown per session, so replaying doesn't feel identical.

---

## VISUAL ASSETS REQUIRED

| File | Description |
|------|-------------|
| `narrative/kitchen.png` | 1280×720. 1950s kitchen. Warm. Slightly wrong. Mom at stove, Dad at table, Christmas tree visible. |
| `narrative/reincarnation_bg.png` | 1280×720. Twin circular View-Master lenses framing a corrupted, static-filled snowy forest. |
| `narrative/family_loop1.png` | 1280×720. Family portrait. MC's eyes violently scribbled out in red. |
| `narrative/family_loop2.png` | Same as above + MC's lower face is smooth featureless skin. No mouth. |
| `narrative/family_loop3.png` | Eyes + mouth gone + MC's torso and face chemically dissolved from photo. |
| `narrative/family_loop_final.png` | MC completely absent. Mom and Dad smiling at empty space. |

*All portrait images must be formatted as `.png` and look like actual vintage 1950s photographs — sepia/desaturated edges, slight overexposure, grain.*