"""
Command line runner for the Music Recommender Simulation.
"""

from src.recommender import load_songs, recommend_songs


def print_recommendations(recommendations, user_prefs):
    width = 60
    print("\n" + "=" * width)
    print("  MUSIC RECOMMENDER - TOP PICKS")
    print("=" * width)
    print(f"  Profile : {user_prefs['genre']} / {user_prefs['mood']}")
    print(f"  Energy  : {user_prefs['energy']}  |  Acoustic: {user_prefs['likes_acoustic']}")
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"\n  #{rank}  {song['title']}  -  {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}  |  Energy: {song['energy']}")
        print(f"       Score: {score:.2f}")
        print(f"       Why  :")
        for reason in explanation.split(", "):
            print(f"              {reason}")

    print("\n" + "=" * width + "\n")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    user_prefs = {
        "genre":          "pop",
        "mood":           "happy",
        "energy":         0.8,
        "valence":        0.8,
        "tempo_bpm":      120,
        "likes_acoustic": False,
        "danceability":   0.75,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(recommendations, user_prefs)


if __name__ == "__main__":
    main()
