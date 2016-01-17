import xml.etree.ElementTree
from sets import Set
import csv
import argparse
from tabulate import tabulate


class Song(object):
    def __init__(self, title, artist, album):
        self.title = title
        self.artist = artist
        self.album = album

    def __repr__(self):
        return "Song(%s, %s, %s)" % (self.title, self.artist, self.album)
        
    def __eq__(self, other):
        if isinstance(other, Song):
            return (self.title.lower() == other.title.lower() and
                    self.artist.lower() == other.artist.lower() and
                    self.album.lower() == other.album.lower())
        else:
            return False
            
    def __ne__(self, other):
        return (not self.__eq__(other))
            
    def __hash__(self):
        return hash(self.__repr__())
        
    def to_array(self):
        return [self.title, self.artist, self.album]
        
def main():
    parser = argparse.ArgumentParser(description='Diffs an iTunes library or playlist with a list of songs from Google Music to see what is different')
    parser.add_argument('google_music_csv_path', metavar="GOOGLE-MUSIC-CSV-PATH", type=str, help='path to csv list of songs on Google Music (generated by https://github.com/mmccoy37/gmusic-csv)')
    parser.add_argument('itunes_library_xml_path', metavar="ITUNES-LIBRARY-XML-PATH", type=str, help='path to iTunes playlist')
    parser.add_argument('-p', '--itunes-playlist-name', dest='itunesPlaylistName', help='name of itunes playlist', metavar='NAME')
    args = parser.parse_args()
    
    googleMusicCsvPath = args.google_music_csv_path
    itunesLibraryXmlPath = args.itunes_library_xml_path
    itunesPlaylistName = args.itunesPlaylistName
    
    #get list of all itunes songs
    itunesLib = xml.etree.ElementTree.parse(itunesLibraryXmlPath).getroot()
    itunesSongSet = Set()
    itunesInvalid = list()
    itunesTrackIdDict = dict()
    for dict1 in itunesLib.findall('dict'):
        for dict2 in dict1.findall('dict'):
            for dict3 in dict2.findall('dict'):
                children = list(dict3)
                childrenText = list()
                for child in children:
                    childrenText.append(child.text)
                try:
                    trackIdIndex = childrenText.index('Track ID')
                    titleIndex = childrenText.index('Name')
                    artistIndex = childrenText.index('Artist')
                    albumIndex = childrenText.index('Album')
                       
                    trackId = childrenText[trackIdIndex + 1]
                    title = childrenText[titleIndex + 1]
                    artist = childrenText[artistIndex + 1]
                    album = childrenText[albumIndex + 1]
                    song = Song(title, artist, album)
                    itunesTrackIdDict[trackId] = song
                    itunesSongSet.add(song)
                except ValueError:
                    titleIndex = childrenText.index('Name')
                    itunesInvalid.append(childrenText[titleIndex + 1])
    
    # special handling for when playlist is defined
    # basically just xml parsing to find the list of all songs in the playlist
    if itunesPlaylistName is not None:
        #shit for playlists
        itunesSongSet = Set()
        for dict1 in itunesLib.findall('dict'):
            for array2 in dict1.findall('array'):
                for dict3 in array2.findall('dict'):
                    children = list(dict3)
                    childrenText = list()
                    for child in children:
                        childrenText.append(child.text)
                    playlistNameIndex = childrenText.index('Name')
                    playlistName = childrenText[playlistNameIndex + 1]
                    if playlistName == itunesPlaylistName:
                        for array4 in dict3.findall('array'):
                            for dict5 in array4.findall('dict'):
                                children = list(dict5)
                                childrenText = list()
                                for child in children:
                                    childrenText.append(child.text)
                                trackIdIndex = childrenText.index('Track ID')
                                trackId = childrenText[trackIdIndex + 1]
                                if trackId in itunesTrackIdDict:
                                    itunesSongSet.add(itunesTrackIdDict[trackId])
                
    #get list of all songs from the list I got from gmusicapi
    gmusicSongSet = Set()
    duplicates = list()
    with open(googleMusicCsvPath) as file:
        reader = csv.reader(file)
        reader.next()
        for line in reader:
            title = line[3].decode('utf-8')
            artist = line[0].decode('utf-8')
            album = line[1].decode('utf-8')
            song = Song(title, artist, album)
            # add song to list of songs in playlist
            if song not in gmusicSongSet:
                gmusicSongSet.add(song)
            # set it as a duplicate song if the song already got added earlier
            else:
                duplicates.append(song.to_array())
    
    accountedFor = []
    notAccountedFor = []
    for song in gmusicSongSet:
        if song in itunesSongSet:
            accountedFor.append(song.to_array())
        else:
            notAccountedFor.append(song.to_array())
        
    for song in itunesSongSet:
        if song in gmusicSongSet:
            if song not in accountedFor:
                accountedFor.append(song.to_array())
        else:
            if song not in notAccountedFor:
                notAccountedFor.append(song.to_array())

    print("Not accounted for:")
    print(tabulate(notAccountedFor, headers=["Title", "Artist", "Album"]))
    print("\nDuplicates:")
    print(tabulate(duplicates, headers=["Title", "Artist", "Album"]))
   
    print("iTunes Songs: " + str(len(itunesSongSet)))
    print("Google Songs: " + str(len(gmusicSongSet)))
    print("Accounted for: " + str(len(accountedFor)))
    print("Unaccounted for: " + str(len(notAccountedFor)))
    
if __name__ == "__main__": main()
