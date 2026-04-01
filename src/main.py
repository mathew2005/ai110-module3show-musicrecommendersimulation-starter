"""
Command line runner for the Music Recommender Simulation.
Runs all standard and adversarial profiles in sequence.
"""

from src.recommender import load_songs, recommend_songs


# ── Standard profiles ────────────────────────────────────────────────────────

HIGH_ENERGY_POP = {
    "label":          "High-Energy Pop",
    "genre":          "pop",
    "mood":           "happy",
    "energy":         0.85,
    "valence":        0.82,
    "tempo_bpm":      125,
    "likes_acoustic": False,
    "danceability":   0.80,
}

CHILL_LOFI = {
    "label":          "Chill Lofi",
    "genre":          "lofi",
    "mood":           "chill",
    "energy":         0.38,
    "valence":        0.58,
    "tempo_bpm":      76,
    "likes_acoustic": True,
    "danceability":   0.55,
}

DEEP_INTENSE_ROCK = {
    "label":          "Deep Intense Rock",
    "genre":          "rock",
    "mood":           "intense",
    "energy":         0.90,
    "valence":        0.40,
    "tempo_bpm":      150,
    "likes_acoustic": False,
    "danceability":   0.60,
}

# ── Adversarial / edge-case profiles ─────────────────────────────────────────

# Edge case 1: conflicting signals — high energy but sad mood
# Expected tension: energy pulls toward loud/fast tracks, mood pulls toward
# slow/sorrowful ones. Does the system surface something coherent?
HIGH_ENERGY_SAD = {
    "label":          "Edge Case: High-Energy + Sad Mood",
    "genre":          "blues",
    "mood":           "sad",
    "energy":         0.90,
    "valence":        0.15,
    "tempo_bpm":      140,
    "likes_acoustic": False,
    "danceability":   0.70,
}

# Edge case 2: genre that does not exist in the catalog
# Expected behavior: genre match is always 0, so the system falls back entirely
# on numeric proximity. Tests whether the catalog still returns anything useful.
UNKNOWN_GENRE = {
    "label":          "Edge Case: Genre Not In Catalog (reggae)",
    "genre":          "reggae",
    "mood":           "happy",
    "energy":         0.65,
    "valence":        0.75,
    "tempo_bpm":      95,
    "likes_acoustic": True,
    "danceability":   0.80,
}

# Edge case 3: perfectly neutral / midpoint preferences
# Everything set to 0.5. No strong pull in any direction.
# Tests whether the system returns a reasonable middle-of-catalog result
# or collapses to arbitrary ordering.
ALL_NEUTRAL = {
    "label":          "Edge Case: All Neutral (0.5 everything)",
    "genre":          "pop",
    "mood":           "happy",
    "energy":         0.5,
    "valence":        0.5,
    "tempo_bpm":      100,
    "likes_acoustic": False,
    "danceability":   0.5,
}

# Edge case 4: extreme acoustic + low energy but aggressive mood
# Acoustic folk texture + angry mood are rarely paired in real music.
# Tests whether mood or acousticness wins when they disagree.
ACOUSTIC_ANGRY = {
    "label":          "Edge Case: Acoustic Texture + Angry Mood",
    "genre":          "metal",
    "mood":           "angry",
    "energy":         0.95,
    "valence":        0.15,
    "tempo_bpm":      165,
    "likes_acoustic": True,   # wants acoustic but metal is almost never acoustic
    "danceability":   0.50,
}


# ── Output formatting ─────────────────────────────────────────────────────────

def print_recommendations(recommendations, profile):
    """Print a labeled, readable block of top-k recommendations for one profile."""
    width = 64
    label = profile.get("label", f"{profile['genre']} / {profile['mood']}")
    print("\n" + "=" * width)
    print(f"  PROFILE: {label}")
    print(f"  genre={profile['genre']}  mood={profile['mood']}  "
          f"energy={profile['energy']}  acoustic={profile['likes_acoustic']}")
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"\n  #{rank}  {song['title']}  -  {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}  |  Energy: {song['energy']}")
        print(f"       Score: {score:.2f}")
        print(f"       Why  :")
        for reason in explanation.split(", "):
            print(f"              {reason}")

    print("\n" + "=" * width)


# ── Runner ────────────────────────────────────────────────────────────────────

def main() -> None:
    """Load catalog and run all standard and adversarial profiles."""
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded songs: {len(songs)}")

    profiles = [
        HIGH_ENERGY_POP,
        CHILL_LOFI,
        DEEP_INTENSE_ROCK,
        HIGH_ENERGY_SAD,
        UNKNOWN_GENRE,
        ALL_NEUTRAL,
        ACOUSTIC_ANGRY,
    ]

    for profile in profiles:
        results = recommend_songs(profile, songs, k=5)
        print_recommendations(results, profile)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Run a single profile by number: python -m src.main 1
        songs = load_songs("data/songs.csv")
        all_profiles = [
            HIGH_ENERGY_POP, CHILL_LOFI, DEEP_INTENSE_ROCK,
            HIGH_ENERGY_SAD, UNKNOWN_GENRE, ALL_NEUTRAL, ACOUSTIC_ANGRY,
        ]
        idx = int(sys.argv[1]) - 1
        profile = all_profiles[idx]
        results = recommend_songs(profile, songs, k=5)
        print(f"\nLoaded songs: {len(songs)}")
        print_recommendations(results, profile)
    else:
        main()
