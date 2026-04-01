# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

This system suggests the top 5 songs from an 18-song catalog that best match a
user's stated taste preferences. It is built for classroom exploration of how
content-based recommendation algorithms work. It is not designed for real users
or production use.

The system assumes the user can describe their preferences in advance using
genre, mood, and numeric sliders for energy and tempo. It does not learn from
listening history or adapt over time.

---

## 3. How the Model Works

Every song in the catalog gets a numeric score that represents how well it
matches the user's preferences. Songs are then sorted from highest to lowest
score, and the top five are returned.

The score has two parts. The first part checks whether the song's genre and
mood exactly match what the user wants. A genre match adds 3 points and a mood
match adds 2 points. These are the strongest signals — if a song gets both, it
starts 5 points ahead of a song with no match.

The second part measures how close each song's audio features are to the user's
targets. For example, if a user wants high-energy music (energy = 0.9) and a
song has energy = 0.91, that is nearly a perfect match and earns close to the
full 2.5 points available for energy. A song with energy = 0.3 would earn much
less. The same "closeness" math applies to mood tone (valence), tempo in beats
per minute, whether the sound is acoustic or electronic, and danceability.

Every recommendation also produces a plain-language breakdown showing exactly
how many points each feature contributed, so the user can see why a song was
recommended.

---

## 4. Data

The catalog contains 18 songs stored in `data/songs.csv`. The original starter
file had 10 songs. Eight additional songs were added to cover genres and moods
not represented in the original set.

**Genres represented:** pop, lofi, rock, jazz, ambient, synthwave, indie pop,
hip-hop, r&b, classical, folk, electronic, metal, blues, country

**Moods represented:** happy, chill, intense, relaxed, focused, moody,
energetic, romantic, melancholic, nostalgic, angry, sad, peaceful

The catalog is very small. Most genres appear only once, which means a user
whose favorite genre is "folk" has only one possible genre match in the entire
catalog. The data was created for a classroom project and does not reflect the
distribution of real listening habits.

---

## 5. Strengths

The system works well when the user's preferences are specific and the catalog
has a clear match. For the rock/intense profile, Storm Runner ranked first by a
large margin because it matched on genre, mood, energy, and tempo all at once.
The recommendations made intuitive sense.

The breakdown feature is a genuine strength. Because every recommendation shows
its point-by-point reasoning, it is easy to understand why a song ranked where
it did. This transparency would be unusual in a real production system.

The system also degrades gracefully. When a user requests a genre that does not
exist in the catalog (tested with "reggae"), the system still returns reasonable
results by falling back on mood and numeric proximity instead of returning an
error or an empty list.

---

## 6. Limitations and Bias

**Genre lock-in is the most significant bias.** Because genre uses an
exact string match worth 3.0 points, a song from an adjacent genre can never
outscore a mediocre song from the correct genre, no matter how well it matches
every other feature. A rock fan will likely enjoy metal, but the system treats
them as completely unrelated. In a real catalog of millions of songs, this would
create a strong filter bubble — the system would never surface anything outside
the one genre the user named at setup.

**The catalog over-represents the original starter genres.** Pop and lofi each
have multiple songs in the catalog (pop has 2, lofi has 3), while most other
genres have exactly one. This means pop and lofi users see more variety in their
top results, while a blues or classical user gets a genre match once and then
falls back to unrelated songs. The system is unintentionally biased toward users
whose taste aligns with the most common genres in the dataset.

**Mood uses exact string matching, which ignores adjacent emotions.** The moods
"chill" and "relaxed" feel nearly identical to most listeners, but the system
scores them as completely different. A user who wants "chill" music scores the
jazz song Coffee Shop Stories (mood: relaxed) as having zero mood match, even
though most people would consider it a perfect fit.

**Conflicting preferences cannot be resolved.** When a user asks for high energy
(0.9) but a sad mood, the system cannot negotiate between those signals. It
picks the song that wins on categorical points (genre + mood) and ignores the
energy conflict. The "high-energy sad" edge case showed Rainy Day Blues ranking
first even though it has energy 0.30 — far from the user's 0.90 target — purely
because genre and mood matched.

**The catalog is too small to show real diversity.** With only 18 songs, a
genre mismatch eliminates most of the catalog immediately. The system was
designed for a much larger dataset where numeric features would do more
differentiation work.

---

## 7. Evaluation

Seven user profiles were tested: three standard profiles (High-Energy Pop,
Chill Lofi, Deep Intense Rock) and four adversarial edge cases.

Two weight experiments were also run to test sensitivity:

**Experiment A — double energy weight, halve genre weight**
(genre: 3.0 → 1.5, energy: 2.5 → 5.0)

| Profile | Original top 3 | Experiment A top 3 |
|---|---|---|
| High-Energy Pop | Sunrise City, Gym Hero, Rooftop Lights | Sunrise City, Rooftop Lights, Gym Hero |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow | Library Rain, Midnight Coding, Focus Flow |
| Deep Intense Rock | Storm Runner, Gym Hero, Iron Verdict | Storm Runner, Gym Hero, Iron Verdict |

Halving the genre weight while doubling energy only swapped ranks 2 and 3 for
the pop profile. The top song did not change in any profile. This shows the
system is not very sensitive to moderate weight changes when the catalog is
small — the best match tends to dominate regardless.

**Experiment B — remove mood check entirely**

| Profile | Original top 3 | No mood top 3 |
|---|---|---|
| High-Energy Pop | Sunrise City, Gym Hero, Rooftop Lights | Sunrise City, Gym Hero, Rooftop Lights |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow | Focus Flow, Library Rain, Midnight Coding |
| Deep Intense Rock | Storm Runner, Gym Hero, Iron Verdict | Storm Runner, Night Drive Loop, Iron Verdict |

Removing mood had more impact. For Chill Lofi, Focus Flow moved from 3rd to 1st
because it no longer lost points for having the wrong mood (focused vs chill).
For Deep Intense Rock, Gym Hero dropped out of the top 3 — it was only there
because of mood match, and without that, Night Drive Loop's numeric proximity
was stronger.

**What surprised me:** Gym Hero (pop/intense, energy 0.93) appears in the top
results for nearly every high-energy profile regardless of genre. It kept
showing up for the rock user, the neutral user, and the pop user. This is the
"filter bubble" in action — one song with strong numeric features and a popular
mood label ends up dominating multiple different user profiles, reducing the
diversity of recommendations.

---

## 8. Future Work

- Replace exact genre matching with a genre similarity map so that rock and
  metal, or lofi and ambient, receive partial credit rather than zero
- Add a diversity penalty so the same song cannot appear in the top results for
  more than two different profiles
- Allow users to specify a range for energy rather than a single target value,
  so "I want something between 0.6 and 0.8" is expressible
- Support multiple genres and moods per profile so a user who listens to both
  jazz on weekdays and pop on weekends gets a blended set of recommendations
- Expand the catalog to at least 100 songs so numeric features have enough
  variation to do meaningful differentiation work

---

## 9. Personal Reflection

Building this recommender made the hidden assumptions in recommendation systems
very visible. Every number — the 3.0 for genre, the 2.5 for energy — is a
judgment call that shapes whose taste the system serves well and whose it
ignores. The genre lock-in bias was not something I designed on purpose; it
emerged from a weight that seemed reasonable in isolation but turned out to
dominate everything else.

The most surprising result was how stable the rankings were when weights
changed. Doubling the energy weight barely moved the top songs. That taught me
that in a small catalog with one clearly dominant match (like Storm Runner for
the rock profile), the scoring formula matters much less than having the right
song in the catalog at all. Real systems need both good algorithms and a big,
diverse catalog — neither alone is enough.

It also changed how I think about Spotify's Discover Weekly. What looks like
intelligent personalization is really a scoring function like this one, just
running on millions of songs and trained on billions of listening events instead
of 18 songs and a hand-written weight table.
