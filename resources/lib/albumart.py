import sys
import os


import time,calendar,traceback
import urllib2,urllib,re,cookielib, string

album_pattern='<td class=\"text-center\">\s+(<a[\"\w\d\!\=< >\/\.]+<\/a>\s+)?<\/td>\s+<td><a href=\"(?P<link>[\/\:\-\w\d\.]+)\">(?P<album>[\w \d\]\[\.\-\?\!\(\)\']+)<\/a><\/td>\s+<td>(?P<artist>[\w\d \!\?\']+)<\/td>'
image_pattern='<div class=\"image\">\s*<img src=\"(?P<link>[\/\:\w\-\d\.]+)\"'
class AlbumArtFetcher(object):
	
	def __init__(self,work_dir,cache):
		self.server_url = 'http://www.allmusic.com'
		self.work_dir=work_dir
		self.cache=cache
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		opener.version = 'User-Agent=Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)'
		urllib2.install_opener(opener)
		
		
	def _get_local_album(self,artist,album):
		if self.cache:
			imagefile = self.get_image_file_name(artist,album)
			if os.path.exists(imagefile):
				print 'Image already downloaded, returning '+imagefile
				return imagefile
		return None

	def get_album_art(self,artist,album):
		try:
			print 'Searching for album art '+str(artist)+' - '+str(album)
			return self._get_album_art(artist,album)
		except:
			print 'Error searching/downloading'
			traceback.print_exc()
			return None

	def _get_album_art(self,artist, album):
		if artist == '' or album == '':
			print 'Nothing to search for'
			return None
		filename = self._get_local_album(artist,album)
		if not filename == None:
			return filename
		url = self.server_url+'/search/album/'+urllib.quote(album)
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		content = response.read()
		response.close()
		link = None
		for matches in re.finditer(album_pattern, content, re.IGNORECASE | re.DOTALL):
#			print 'Match: '+ matches.group('artist')+ ' '+matches.group('album')
#			print matches.group(0)
#			print matches.group('artist')
#			print matches.group('link')
			if string.lower(artist) == string.lower(matches.group('artist')):
#				print matches.group('link')
				link = matches.group('link')
				break
		if link == None:
			print 'No results found'
			return None
		response = urllib2.urlopen(link)
		content = response.read()
		response.close()		
		for matches in re.finditer(image_pattern, content, re.IGNORECASE | re.DOTALL):
#			print matches.group('link')
			filename = self.get_image_file_name(artist,album)
			if not self.cache:
				filename = os.path.join(self.work_dir,'album.jpg')
			f = open(filename,'w')
			f.write(self._get_file(matches.group('link')))
			f.close()
			print 'Image downloaded'
			return filename
		return None

	def get_image_file_name(self,artist,album):
		return os.path.join(self.work_dir,artist+'-'+album+'.jpg')
					
	def _get_file(self,url):
		if not url.startswith('http://'):
			url = self.server_url+url
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		content = response.read()
		response.close()
		return content
				