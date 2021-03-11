import spotipy
import time
import xml.etree.ElementTree as ET

from spotipy.oauth2 import SpotifyOAuth
from secrets import cid, secret, redirect_uri, scope, name, description, xmlfile


class CreatePlaylist:
    def __init__(self):
        self.uris_to_add = []
        self.total_songs_added = 0
        self.playlist_name = name
        self.playlist_description = description
        auth_manager = SpotifyOAuth(client_id=cid,
                                    client_secret=secret,
                                    redirect_uri=redirect_uri,
                                    scope=scope)
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def create_playlist(self):
        playlist_id = ''
        user_id = self.sp.me()['id']
        self.sp.user_playlist_create(user_id, self.playlist_name, description=self.playlist_description)

        time.sleep(1)

        user_playlists = self.sp.user_playlists(user_id)
        for playlist in user_playlists['items']:
            if playlist['name'] == self.playlist_name:
                playlist_id = playlist['id']
                break

        if playlist_id:
            self.uri_manager_for_playlist(playlist_id)
        else:
            print(f'Playlist {self.playlist_name} was not created or not available')

    def uri_manager_for_playlist(self, playlist_id):
        tree = ET.parse(xmlfile)
        root = tree.getroot()

        for element in root[0][17].findall('dict'):
            song_name = element[3].text.lower()
            artist_name = element[5].text.split()
            song_to_parse = song_name.split("(")
            if len(song_to_parse) > 1:
                for item in song_to_parse:
                    if item.find("remix") != -1:
                        song_name = f"{song_to_parse[0]} {item}"
                        break
                    else:
                        song_name = song_to_parse[0]

            id_result = self.get_spotify_uri(song_name, artist_name[0])

            if id_result is None:
                print(f'{element[3].text} not added.')
            else:
                self.uris_to_add.append(id_result)
                self.total_songs_added += 1

            if len(self.uris_to_add) == 49:
                self.add_song_to_playlist(playlist_id)
                self.uris_to_add.clear()

        if self.uris_to_add:
            self.add_song_to_playlist(playlist_id)

        print(f'Se añadieron {self.total_songs_added} canciones a {self.playlist_name}.')

    def get_spotify_uri(self, song_name, artist):
        query = song_name + " " + artist
        try:
            result = self.sp.search(q=query, limit=3, offset=0)
            for song in result["tracks"]["items"]:
                for item in song["artists"]:
                    temp_name = item["name"].lower()
                    if temp_name.find(artist.lower()) != -1:
                        return song["id"]
        except IndexError:
            print(f'I couldn\'t find uris for {song_name} inside Spotify.')
            return None
        except Exception as e:
            print(f'Something went wrong with {song_name}. Error: {e}')
            return None

    def add_song_to_playlist(self, playlist_id):
        self.sp.playlist_add_items(playlist_id, self.uris_to_add)


if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.create_playlist()


