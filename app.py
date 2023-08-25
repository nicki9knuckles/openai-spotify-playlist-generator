import openai
import os
import json
from dotenv import load_dotenv
import os
import argparse
import spotipy
import datetime


def main():
    load_dotenv(".env")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    parser = argparse.ArgumentParser(
        description="Generate a playlist based on a prompt"
    )
    parser.add_argument(
        "-p", default="BotList", type=str, help="Prompt to generate playlist from"
    )
    parser.add_argument(
        "-n",
        type=int,
        default=10,
        help="The number of songs to generate for the playlist",
    )
    args = parser.parse_args()

    playlist_prompt = args.p
    count = args.n
    playlist = get_playlist(playlist_prompt, count)
    add_songs_to_spotify(playlist_prompt, playlist)


def add_songs_to_spotify(playlist_prompt, playlist):
    # Sign up as a developer and register your app at https://developer.spotify.com/dashboard/applications

    # Step 1. Create an Application.

    # Step 2. Copy your Client ID and Client Secret.
    spotipy_client_id = os.getenv(
        "SPOTIFY_CLIENT_ID"
    )  # Use your Spotify API's keypair's Client ID
    spotipy_client_secret = os.getenv(
        "SPOTIFY_CLIENT_SECRET"
    )  # Use your Spotify API's keypair's Client Secret

    # Step 3. Click `Edit Settings`, add `http://localhost:9999` as as a "Redirect URI"
    spotipy_redirect_url = "http://localhost:9999"  # Your browser will return page not found at this step. We'll grab the URL and paste back in to our console

    # Step 4. Click `Users and Access`. Add your Spotify account to the list of users (identified by your email address)

    # Spotipy Documentation
    # https://spotipy.readthedocs.io/en/2.22.1/#getting-started

    sp = spotipy.Spotify(
        auth_manager=spotipy.SpotifyOAuth(
            client_id=spotipy_client_id,
            client_secret=spotipy_client_secret,
            redirect_uri=spotipy_redirect_url,
            scope="playlist-modify-private",
        )
    )
    current_user = sp.current_user()
    assert current_user is not None

    track_ids = []

    for item in playlist:
        artist, song = item["artist"], item["song"]
        query = f"{song} {artist}"
        search_results = sp.search(q={query}, type="track", limit=10)
        track_ids.append(search_results["tracks"]["items"][0]["id"])

    created_playlist = sp.user_playlist_create(
        current_user["id"],
        public=False,
        name=f"{playlist_prompt} ({datetime.datetime.now().strftime('%c')})",
    )

    sp.user_playlist_add_tracks(current_user["id"], created_playlist["id"], track_ids)


def get_playlist(prompt="BotList", count=10):
    example_json = """
    [
      {"song": "Hurt", "artist": "Johnny Cash"},
      {"song": "Someone Like You", "artist": "Adele"},
      {"song": "Mad World", "artist": "Gary Jules"},
      {"song": "Nothing Compares 2 U", "artist": "Sinéad O'Connor"},
      {"song": "Yesterday", "artist": "The Beatles"}
    ]
  """

    messages = [
        {
            "role": "system",
            "content": """
            You are a helpful playlist, generating assistant. 
            You should generate a list of songs in their artists according to a text prompt.
            You should return ONLY a JSON array (with no other text) where each element follows this format:
            {"song": <song_title>, "artist": <artist_name>}
          """,
        },
        {
            "role": "user",
            "content": "Generate a playlist of 5 songs and artists based on this prompt: super super sad songs",
        },
        {
            "role": "assistant",
            "content": example_json,
        },
        {
            "role": "user",
            "content": f"Generate a playlist of {count} songs and artists based on this prompt: {prompt}",
        },
    ]

    res = openai.ChatCompletion.create(
        messages=messages,
        model="gpt-3.5-turbo",
        max_tokens=400,
    )

    playlist = json.loads(res["choices"][0]["message"]["content"])
    return playlist


if __name__ == "__main__":
    main()
