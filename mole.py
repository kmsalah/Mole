
# modules we're using (you'll need to download lxml)
import lxml.html, urllib2, urlparse
import PyPDF2
import re
from StringIO import StringIO
import sys

if len(sys.argv) != 3:
	print("\n Error: Enter only one url to scrape and one keyword to search.") 
	sys.exit()

# the url of the page you want to scrape
base_url = sys.argv[1]

# fetch the page
res = urllib2.urlopen(base_url)

# parse the response into an xml tree
tree = lxml.html.fromstring(res.read())

# construct a namespace dictionary to pass to the xpath() call
# this lets us use regular expressions in the xpath
ns = {'re': 'http://exslt.org/regular-expressions'}

# iterate over all <a> tags whose href ends in ".pdf" (case-insensitive)
pdf_links = []
for node in tree.xpath('//a[re:test(@href, "\.pdf$", "i")]', namespaces=ns):

    # print the href, joining it to the base_url
    pdf_links.append(urlparse.urljoin(base_url, node.attrib['href']))


found_links = []
# open the pdf file
for pdf_link in pdf_links:
	try:
		remoteFile = urllib2.urlopen(urllib2.Request(pdf_link)).read()
		memoryFile = StringIO(remoteFile)

		object = PyPDF2.PdfFileReader(memoryFile)

		# get number of pages
		NumPages = object.getNumPages()

		# define keyterms
		keyword = sys.argv[2]
		# extract text and do the search
		for i in range(0, NumPages):
			PageObj = object.getPage(i)
			Text = PageObj.extractText() 
			# print(Text)
			ResSearch = re.search(keyword, Text)
			if ResSearch is not None:
				found_links.append(pdf_link)
				break
	#these errors should be further investigated
	except urllib2.HTTPError:
		print("HTTPError: " + pdf_link)
		continue
	except urllib2.URLError:
		print("URLError: " + pdf_link)
		continue

print("Links that contain the keyword:")
print(found_links)
