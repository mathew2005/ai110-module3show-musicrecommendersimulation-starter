import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ─── WEIGHTS ──────────────────────────────────────────────────────────────────
# Finalized after comparing three schemes on the 18-song catalog:
#
#   Starter (genre+2, mood+1)  -> separation gap 4.81 between best/worst match
#   Current (genre+3, mood+2)  -> separation gap 8.08  <-- chosen
#   Flat (all equal)           -> separation gap 3.96
#
# Genre (3.0) > Mood (2.0): genre is a hard catalog filter. A wrong genre is
#   always a bad recommendation regardless of energy or mood. Mood is a gradient
#   where adjacent values (chill/relaxed, intense/energetic) can still feel right.
#
# Energy (2.5) > Valence (2.0): energy spans 0.22-0.97 in this catalog, the
#   widest effective range of any numeric feature, making it the best discriminator.
#
# Danceability (0.5) is lowest because it is highly correlated with energy+tempo.
#   It adds almost no unique information once those two are already weighted.

WEIGHTS = {
    "genre":        3.0,   # categorical: hard catalog filter
    "mood":         2.0,   # categorical: emotional state
    "energy":       2.5,   # numerical: widest range, strongest discriminator
    "valence":      2.0,   # numerical: happy vs. brooding
    "acousticness": 1.5,   # numerical: organic vs. electronic texture
    "tempo_bpm":    1.0,   # numerical: activity context, normalized over 100 BPM
    "danceability": 0.5,   # numerical: correlated with energy+tempo, low unique value
}

# Maximum BPM spread used to normalize tempo proximity to [0, 1]
_TEMPO_SPREAD = 100.0


# ─── SCORING RULE ─────────────────────────────────────────────────────────────

def _proximity(value: float, target: float) -> float:
    """Return 1 - |value - target|, giving 1.0 on exact match and 0.0 at maximum distance."""
    return 1.0 - abs(value - target)


def _tempo_proximity(bpm: float, target_bpm: float) -> float:
    """Return BPM proximity normalized over a 100-BPM spread, clamped to [0, 1]."""
    return max(0.0, 1.0 - abs(bpm - target_bpm) / _TEMPO_SPREAD)


def score_song(song: Dict, user_prefs: Dict) -> Tuple[float, str]:
    """
    SCORING RULE — rates a single song against user preferences.

    Categorical features contribute a fixed bonus on exact match.
    Numerical features use proximity scoring: closer to the user's
    target = higher contribution. Each contribution is multiplied by
    its weight before being added to the total.

    Returns:
        (score, explanation) where explanation is a comma-separated string
        listing every feature's contribution with its point value, e.g.:
        "genre match (+3.0), energy proximity (+2.35), mood no match (+0.0)"
    """
    score = 0.0
    reasons = []

    # --- Categorical: binary match bonuses ---
    genre_pts = WEIGHTS["genre"] if song.get("genre") == user_prefs.get("genre") else 0.0
    score += genre_pts
    reasons.append(f"genre match (+{genre_pts:.1f})")

    mood_pts = WEIGHTS["mood"] if song.get("mood") == user_prefs.get("mood") else 0.0
    score += mood_pts
    reasons.append(f"mood match (+{mood_pts:.1f})")

    # --- Numerical: proximity × weight ---
    if "energy" in user_prefs:
        p = _proximity(song["energy"], user_prefs["energy"])
        pts = round(p * WEIGHTS["energy"], 2)
        score += pts
        reasons.append(f"energy proximity (+{pts:.2f})")

    if "valence" in user_prefs:
        p = _proximity(song["valence"], user_prefs["valence"])
        pts = round(p * WEIGHTS["valence"], 2)
        score += pts
        reasons.append(f"valence proximity (+{pts:.2f})")

    if "tempo_bpm" in user_prefs:
        p = _tempo_proximity(song["tempo_bpm"], user_prefs["tempo_bpm"])
        pts = round(p * WEIGHTS["tempo_bpm"], 2)
        score += pts
        reasons.append(f"tempo proximity (+{pts:.2f})")

    if "danceability" in user_prefs:
        p = _proximity(song["danceability"], user_prefs["danceability"])
        pts = round(p * WEIGHTS["danceability"], 2)
        score += pts
        reasons.append(f"danceability proximity (+{pts:.2f})")

    # --- Acoustic preference: bool → target value (0.8 acoustic / 0.2 electronic) ---
    if "likes_acoustic" in user_prefs:
        target_acoustic = 0.8 if user_prefs["likes_acoustic"] else 0.2
        p = _proximity(song["acousticness"], target_acoustic)
        pts = round(p * WEIGHTS["acousticness"], 2)
        score += pts
        reasons.append(f"acousticness proximity (+{pts:.2f})")

    explanation = ", ".join(reasons)
    return round(score, 4), explanation


# ─── RANKING RULE ─────────────────────────────────────────────────────────────

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    RANKING RULE — applies the scoring rule to every song, then sorts
    the results by score (highest first) and returns the top-k.

    Why we need both rules:
      • The scoring rule answers "how good is THIS song?" for one item.
      • The ranking rule answers "which songs should come FIRST?" across
        the whole catalog. Score individually, rank collectively.

    Returns:
        List of (song_dict, score, explanation) tuples, best match first.
    """
    scored = [(song, *score_song(song, user_prefs)) for song in songs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


# ─── CSV LOADER ───────────────────────────────────────────────────────────────

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file into a list of dicts with typed fields.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"].strip(),
                "mood":         row["mood"].strip(),
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


# ─── OOP WRAPPER (required by tests/test_recommender.py) ──────────────────────

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Wraps score_song / recommend_songs for the Song / UserProfile dataclasses.
    """

    def __init__(self, songs: List[Song]):
        """Store the catalog of Song objects for scoring and ranking."""
        self.songs = songs

    # Internal helpers to bridge dataclasses ↔ dict-based scoring functions
    def _profile_to_prefs(self, user: UserProfile) -> Dict:
        """Convert a UserProfile dataclass into the dict format expected by score_song."""
        return {
            "genre":         user.favorite_genre,
            "mood":          user.favorite_mood,
            "energy":        user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

    def _song_to_dict(self, song: Song) -> Dict:
        """Convert a Song dataclass into the dict format expected by score_song."""
        return {
            "id":           song.id,
            "title":        song.title,
            "artist":       song.artist,
            "genre":        song.genre,
            "mood":         song.mood,
            "energy":       song.energy,
            "tempo_bpm":    song.tempo_bpm,
            "valence":      song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k Song objects sorted by score (best first)."""
        prefs = self._profile_to_prefs(user)
        scored = [
            (song, score_song(self._song_to_dict(song), prefs)[0])
            for song in self.songs
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation for why a song was recommended."""
        prefs = self._profile_to_prefs(user)
        _, explanation = score_song(self._song_to_dict(song), prefs)
        return explanation
