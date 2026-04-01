# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder takes a user's music preferences (genre, mood, energy level, and a
few other audio traits) and returns the top 5 songs from a small catalog that
best match those preferences. It does not learn from listening history. It just
compares what the user says they want against what each song sounds like, and
picks the closest matches.

---

## 3. Data Used

The catalog is 18 songs stored in `data/songs.csv`. The original project starter
had 10 songs. Eight more were added to cover genres and moods that were missing.

Each song has these features: genre, mood, energy (0 to 1), tempo in BPM,
valence (how happy or sad it sounds, 0 to 1), danceability (0 to 1), and
acousticness (0 to 1).

**Genres in the catalog:** pop, lofi, rock, jazz, ambient, synthwave, indie pop,
hip-hop, r&b, classical, folk, electronic, metal, blues, country

**Moods in the catalog:** happy, chill, intense, relaxed, focused, moody,
energetic, romantic, melancholic, nostalgic, angry, sad, peaceful

**Limits:** The catalog is very small. Most genres only appear once. This means
a folk or blues user gets exactly one genre match and then the system runs out
of catalog. The data was created for a classroom project, not from real
listening habits.

---

## 4. Algorithm Summary

The system scores every song in the catalog against the user's preferences, then
sorts the scores to find the best matches.

Scoring works in two steps.

First, it checks two things that are either a match or not: genre and mood. A
genre match adds 3 points. A mood match adds 2 points. If a song gets both, it
starts with 5 points before anything else is counted.

Second, it checks how close the song's audio numbers are to what the user wants.
For example, if the user wants high energy (0.9) and a song has energy 0.91,
that is almost perfect and earns close to the full 2.5 points. A song with
energy 0.3 earns much less. The same closeness math is applied to valence,
tempo, acousticness, and danceability with different point caps for each.

The total score is the sum of all these contributions. Songs are sorted from
highest to lowest, and the top 5 are shown with a plain-English breakdown of
what earned each point.

---

## 5. Observed Behavior / Biases

**Genre dominates everything.** Genre is worth 3 points on an exact match, which
is the single biggest contributor in the whole formula. A pop song that matches
genre but has the wrong mood still beats a perfect-mood song from any other
genre. This creates a filter bubble: users only see songs from one genre unless
the catalog has no match at all.

**Gym Hero shows up everywhere.** Gym Hero (pop/intense, energy 0.93) appeared
in the top results for the pop user, the rock user, and the neutral user. It has
strong numeric features and a common mood label, so it keeps drifting into
results for people who did not ask for it. This is the filter bubble in action.

**Adjacent moods get zero credit.** "Chill" and "relaxed" feel nearly the same
to most people, but the system treats them as completely different. A chill-
seeking user gives Coffee Shop Stories (mood: relaxed) zero mood points even
though it would feel like a perfect fit.

**Conflicting preferences break the ranking logic.** When a user asked for high
energy (0.9) and a sad mood, the system picked Rainy Day Blues (energy: 0.3) as
the top result because it matched genre and mood. The energy mismatch was
ignored. The system has no way to negotiate when two signals point in opposite
directions.

---

## 6. Evaluation Process

Seven user profiles were tested in total.

**Standard profiles:**
- High-Energy Pop (genre: pop, mood: happy, energy: 0.85)
- Chill Lofi (genre: lofi, mood: chill, energy: 0.38)
- Deep Intense Rock (genre: rock, mood: intense, energy: 0.90)

**Adversarial / edge case profiles:**
- High energy + sad mood (conflicting signals)
- Genre not in catalog ("reggae")
- All preferences set to 0.5 (neutral)
- Acoustic texture preference + angry metal mood (contradictory)

**Experiment A: halved genre weight, doubled energy weight**
The top-ranked song did not change for any profile. Only one rank-2 / rank-3
swap happened. Conclusion: weight changes matter less than catalog content when
the catalog is small.

**Experiment B: mood check removed entirely**
This had more impact. For the Chill Lofi profile, Focus Flow jumped from 3rd to
1st. For Deep Intense Rock, Gym Hero fell out of the top 3. Mood was doing real
work in both of those profiles.

**What matched intuition:** The three standard profiles all returned results that
made sense. Storm Runner for rock, Library Rain for lofi, Sunrise City for pop.

**What surprised me:** How stable the rankings were across weight changes.
Doubling the energy weight barely moved the results. A small catalog with one
clearly dominant song means the algorithm matters less than having the right
songs available.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
This system is for learning how content-based recommendation algorithms work.
It is meant to be run locally by a student or developer who wants to see how
scoring rules translate user preferences into ranked song lists.

**Not intended for:**
- Real music apps or production environments
- Users who expect personalized recommendations based on listening history
- Any situation where the recommendations could influence purchasing, mood, or
  mental health decisions
- Representing actual user diversity or musical taste at scale

The catalog of 18 songs is not representative of any real music library. Do not
use this system to make decisions about what music real people should hear.

---

## 8. Ideas for Improvement

**Replace exact genre matching with a similarity map.** Rock and metal should
share partial credit. Lofi and ambient should too. An exact string match is too
rigid for real taste.

**Add a diversity penalty.** If the same song (like Gym Hero) keeps appearing
for multiple different profiles, it should be penalized so other songs get a
chance. Good recommendations should surface variety, not just the numerically
strongest track.

**Let users specify a range instead of a single target.** Instead of
"energy: 0.8", allow "energy: 0.7 to 0.9". This would make the scoring more
forgiving and reduce the chance that a slightly-off song gets unfairly penalized.

---

## 9. Personal Reflection

**Biggest learning moment:** Every number in the scoring formula is a judgment
call. The 3.0 for genre, the 2.5 for energy — I picked those numbers, and they
shaped whose taste the system served well and whose it ignored. The genre bias
was not intentional. It came from a weight that seemed reasonable but turned out
to dominate everything else. That is exactly how real algorithmic bias works: it
is not usually someone deciding to discriminate, it is someone making a design
choice that has uneven effects they did not foresee.

**How AI tools helped, and when I had to check them:** AI was useful for
generating the additional CSV songs, structuring the scoring formula, and
drafting the README sections quickly. Where I had to double-check was the weight
rationale. The AI suggested reasonable-sounding weights but I had to actually
run the experiments to see whether they produced good results. The data showed
that halving the genre weight barely changed anything — which was surprising and
would not have been obvious from the code alone.

**What surprised me about simple algorithms:** The results felt like real
recommendations. Sunrise City for a pop/happy user, Storm Runner for a
rock/intense user — those are intuitive. It felt smarter than it was. The
system has no understanding of music at all. It is just arithmetic. But because
the features were chosen carefully and the weights were tuned, the output looked
like it understood what the user wanted. That gap between what an algorithm
actually does and what it appears to do is important to keep in mind when
evaluating any AI system.

**What I would try next:** I would add a genre similarity map as the first
improvement. The filter bubble caused by exact genre matching is the most
damaging flaw in the current system. After that, I would expand the catalog to
at least 100 songs so the numeric features have enough variation to do real
work, and the system stops relying so heavily on the categorical match to
differentiate results.
