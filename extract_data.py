# -*- coding: utf-8 -*-
import sqlite3
import pickle
import HTMLParser

import matplotlib.pyplot as plt
import numpy as np

# global variables for filnames
lib_file = 'itunesData.xml'
db_file = 'itunesData.db'
pickled_data = 'itunesData.p'


def pickle_data():
    """
    Pickle the data in a dictionary
    """
    h = HTMLParser.HTMLParser()

    int_len = len('</key><integer>')
    close_int_len = len('</integer>')

    str_len = len('</key><string>')
    close_str_len = len('</string>')

    track_count = 0
    track_data = {}

    for line in open(lib_file, 'r'):
        line = line.strip()

        # ignore all playlist data, only concerned with individual tracks
        if line[5:] == 'Playlists</key>':
            break

        # now we are in a track dict
        if line[5:13] == 'Track ID':
            track_id = int(line[13 + int_len : -close_int_len])
            track_count += 1

            # deal with missing data by setting defaults here
            play_count = 0
            year = 'NULL' 
            album = 'NULL'
            genre = 'NULL'

        elif line[5:9] == 'Name':
            name = line[9 + str_len : -close_str_len]
            name = name.decode('latin-1')
            name = h.unescape(name)

        elif line[5:11] == 'Artist':
            artist = line[11 + str_len : -close_str_len]
            artist = artist.decode('latin-1')
            artist = h.unescape(artist)

        elif line[5:10] == 'Album':
            album = line[10 + str_len : -close_str_len]
            album = album.decode('latin-1')
            album = h.unescape(album)

        elif line[5:10] == 'Genre':
            genre = line[10 + str_len : -close_str_len]
            genre = genre.decode('latin-1')
            genre = h.unescape(genre)

        elif line[5:9] == 'Year':
            year = int(line[9 + int_len : -close_int_len])

        elif line[5:15] == 'Total Time':
            track_length = int(line[15 + int_len : -close_int_len])
            # track length is in milliseconds, lets convert to seconds
            track_length /= 1000

        elif line[5:15] == 'Play Count':
            play_count = int(line[15 + int_len : -close_int_len])

        # add everything to dict once we are at the end of the track data
        elif line == '</dict>':
            #print track_id, name, artist, album, year, play_count

            # add to dict
            # itunes stores some weird hex characters so make sure to decode everything into unicode 
            track_data.update({track_id: {'name': name,
                                          'artist': artist,
                                          'album': album,
                                          'genre': genre,
                                          'year': year,
                                          'length': track_length,
                                          'play_count': play_count}})

    pickle.dump(track_data, open(pickled_data, 'wb'))


def create_db():
    """
    Set up db and populate from pickle
    """
    data_dict = pickle.load(open(pickled_data, 'r'))

    with sqlite3.connect(db_file) as db:
        cursor = db.cursor()

        # drop table if it exists
        try:
            cursor.execute('DROP TABLE tracks;');
        except:
            pass

        # create tracks table
        cursor.execute('''CREATE TABLE tracks(uid INTEGER PRIMARY KEY,
                                              track_id INTEGER,
                                              name TEXT,
                                              artist TEXT,
                                              album TEXT,
                                              genre TEXT,
                                              year INTEGER,
                                              length INTEGER,
                                              play_count INTEGER);''')

        # loop through all tracks and add to db
        for k in data_dict.keys():
            track = data_dict[k]
            try:
                cursor.execute('''INSERT INTO tracks VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?);''',
                                  (k,
                                   track['name'],
                                   track['artist'],
                                   track['album'],
                                   track['genre'],
                                   track['year'],
                                   track['length'],
                                   track['play_count']))
            except:
                print track
                return False


def counts_by_artist():
    """
    Query count of plays by artist
    """
    with sqlite3.connect(db_file) as db:
        cursor = db.cursor()

        cursor.execute('''SELECT artist, SUM(play_count) as count
                          FROM tracks
                          GROUP BY artist
                          ORDER by count DESC
                          LIMIT 50;''')
        results = cursor.fetchall()

    return results


def counts_by_track():
    """
    Query count of plays by artist
    """
    with sqlite3.connect(db_file) as db:
        cursor = db.cursor()

        # concatenate in SQLite with ||
        cursor.execute('''SELECT artist || ' - ' || name, play_count
                          FROM tracks
                          ORDER by play_count DESC
                          LIMIT 50;''')
        results = cursor.fetchall()

    return results


def time_by_artist():
    """
    Query total play time by artist
    """
    with sqlite3.connect(db_file) as db:
        cursor = db.cursor()

        cursor.execute('''SELECT artist, SUM(play_count * length)/60 as play_time 
                          FROM tracks
                          GROUP BY artist
                          ORDER by play_time DESC
                          LIMIT 50;''')
        results = cursor.fetchall()

    return results


def plot_artist_stuff(query):
    """
    Plot some artist stuff!
    """
    # first retrieve data
    results = list(reversed(query()))

    # split into labels and values
    artists = [r[0] for r in results]
    counts = [r[1] for r in results]

    # set positions for bars
    y_pos = np.arange(50)
    y_labels_pos = np.add(y_pos, 0.5)

    # plot it
    plt.barh(y_pos, counts)

    # add artist labels to plot
    plt.yticks(y_labels_pos, artists)
    plt.ylim(0, 50)

    plt.xlabel('Total Plays')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    #pickle_data()
    #create_db()
    plot_artist_stuff(counts_by_track)
