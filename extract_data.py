#import sqlite3
#import xml.etree.cElementTree as ET     # C version is much faster

lib_file = 'libraryData.xml'

int_len = len('</key><integer>')
close_int_len = len('</integer>')

str_len = len('</key><string>')
close_str_len = len('</string>')

track_count = 0
play_count = 0
year = 'NO YEAR' 
album = 'NO ALBUM NAME'

for line in open(lib_file, 'r'):
    line = line.strip()

    # ignore all playlist data, only concerned with individual tracks
    if line[5:] == 'Playlists</key>':
        break

    # now we are in a track dict
    if line[5:13] == 'Track ID':
        track_id = line[13 + int_len : -close_int_len]
        track_count += 1

    elif line[5:9] == 'Name':
        name = line[9 + str_len : -close_str_len]

    elif line[5:11] == 'Artist':
        artist = line[11 + str_len : -close_str_len]

    elif line[5:10] == 'Album':
        album = line[10 + str_len : -close_str_len]

    if line[5:9] == 'Year':
        year = line[9 + int_len : -close_int_len]

    elif line[5:15] == 'Play Count':
        play_count = line[15 + int_len : -close_int_len]

    # print everything once we are at the end of the track data
    elif line == '</dict>':
        print track_id, name, artist, album, year, play_count

        # deal with missing data by setting defaults here
        play_count = 0
        year = 'NO YEAR' 
        album = 'NO ALBUM NAME'

print 'track count =', track_count
