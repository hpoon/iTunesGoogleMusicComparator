import xml.etree.ElementTree
from sets import Set
import csv

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
		
#get list of all itunes songs
itunesLib = xml.etree.ElementTree.parse("C:\\Users\\hp\\Music\\iTunes\\iTunes Music Library.xml").getroot()
itunesSongList = Set()
itunesInvalid = list()
itunesTrackIdDict = dict()
#shit for all songs in library
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
				itunesSongList.add(song)
			except ValueError:
				titleIndex = childrenText.index('Name')
				itunesInvalid.append(childrenText[titleIndex + 1])

#shit for playlists
'''itunesSongList = Set()
for dict1 in itunesLib.findall('dict'):
	for array2 in dict1.findall('array'):
		for dict3 in array2.findall('dict'):
			children = list(dict3)
			childrenText = list()
			for child in children:
				childrenText.append(child.text)
			playlistNameIndex = childrenText.index('Name')
			playlistName = childrenText[playlistNameIndex + 1]
			#playlist name is called "1"
			if playlistName == "1":
				for array4 in dict3.findall('array'):
					for dict5 in array4.findall('dict'):
						children = list(dict5)
						childrenText = list()
						for child in children:
							childrenText.append(child.text)
						trackIdIndex = childrenText.index('Track ID')
						trackId = childrenText[trackIdIndex + 1]
						if trackId in itunesTrackIdDict:
							itunesSongList.add(itunesTrackIdDict[trackId])'''
				
#get list of all songs from the list I got from gmusicapi
gmusicSongList = Set()
duplicates = list()
with open("C:\\Users\\hp\\Desktop\\gmusic-csv\\list.csv") as file:
	reader = csv.reader(file)
	reader.next()
	for line in reader:
		title = line[3].decode('utf-8')
		artist = line[0].decode('utf-8')
		album = line[1].decode('utf-8')
		song = Song(title, artist, album)
		if song not in gmusicSongList:
			gmusicSongList.add(song)
		else:
			duplicates.append(song)
	
accountedFor = Set()
notAccountedFor = Set()
for song in gmusicSongList:
	if song in itunesSongList:
		accountedFor.add(song)
	else:
		notAccountedFor.add(song)
		
for song in itunesSongList:
	if song in gmusicSongList:
		if song not in accountedFor:
			accountedFor.add(song)
	else:
		if song not in notAccountedFor:
			notAccountedFor.add(song)

print("Not accounted for:")
for song in notAccountedFor:
	print("Title: " + song.title + "\t\tArtist: " + song.artist + "\t\tAlbum: " + song.album)
print("\nDuplicates:")
for song in duplicates:
	print("Title: " + song.title + "\t\tArtist: " + song.artist + "\t\tAlbum: " + song.album)
	
print("iTunes Songs: " + str(len(itunesSongList)))
print("Google Songs: " + str(len(gmusicSongList)))
print("Accounted for: " + str(len(accountedFor)))
print("Unaccounted for: " + str(len(notAccountedFor)))