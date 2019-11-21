# encoding: utf-8

import re
import urllib.request
from bs4 import BeautifulSoup
import pypandoc

headers = {}
headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0"

class MyHTTP(urllib.request.HTTPHandler):
    def http_request(self, req):
        req.headers = headers
        return super().http_request(req)
opener = urllib.request.build_opener(MyHTTP())

POST_IDXS = [
#    22, # Mattis, Let the Games Begin
 #   32, # Tiago, Wiktionary
#    58, # Mattis, Exporting sublists
#    384, # Mattis, CLICS
#    445, # Mattis, CLDF
#    477, # Mattis, consonant class matching
#    570, # Nathanael, annotation
#    998, # Mattis, consonant clusters
#    803, # Gereon, fieldwork 1
#    1169, # Nathanael, promiscuity
#    849, # Gereon, Fieldwork 2
#    1668, # Mattis, merging datasets
    867, # Gereon, Fieldwork 3
    1802, # Mattis, Automatic Inference Sound Correspondence
    1807, # Mattis, Inference Sound Correspondence #2
    1823, # Mattis, Inference Sound Correspondence #3
    1820, # Tiago, using pyconcepticon
    1844, # Tiago, using pyconcepticon #2
    1882, # Mattis, behind sino-tibetan
    1866, # Nathanael, biological metaphors #1
    1899, # jaeger, MADness
    1933, # mattis, behind sino-tibetan #3
    1941, # mattis, waterman-eggert
    1962, # mattis, feature alignment #1
    1971, # mattis, feature alignment #2
    1951, # nathanael, biologicla metaphors #2
    1980, # tiago, data reuse
    2000, # nathanael, biological metaphors #3

]

# converts the HTML contents of a post to markdown, taking care of
# all the necessary and common manipulations
def post2md(post_html):
    md_text = pypandoc.convert_text(post_html, 'md', format='html')

    lines = md_text.split('\n')

    # the first line contains the title and the second one contains the
    # header info, but we can add it later fetching from the html page itself
    lines = lines[2:]

    # Remove html left-overs
    lines = [line for line in lines if
        line != '::: {.entry-content}']

    lines = [line for line in lines if
        not line.startswith('[ ]{#more-')]

    # fix problems with BS4 rendering of typeface texts, but make sure
    # this is only applied to non-code blocks
    new_lines = []
    for line in lines:
        # general replacements
        line = line.replace('{style="font-size: 10pt"}', '')

        # only in non_code
        if line.startswith('    '):
            new_lines.append(line)
        else:
            line = re.sub('`\s\s+', '`', line)
            line = re.sub('\s\s+`', '`', line)
            line = line.replace('` -', '`-')
            new_lines.append(line)
    lines = new_lines

    # Remove contents from social media
    new_lines = []
    for line in lines:
        if line.startswith('----------------------------------'):
            break
        else:
            new_lines.append(line)
    lines = new_lines

    # join into a single string and do replacements to fix WP/BS4 problems
    # of breaking punctuation with newlines; this won't affect code
    # as, thanks to markdown, we always have the preceding spaces
    md_text = '\n'.join(lines)

    md_text = md_text.replace('\n,', ',')
    md_text = md_text.replace('\n.', '.')
    md_text = md_text.replace('\n-', '-')

    return md_text

# Builds and MD output from a `post` structure
def build_output(post):
    buf = "# %s\n\n**%s** (%s)\n\n" % \
        (post['title'], post['author'], post['date_published'])#, post['date_updated'])
    print(post['tags'])
    buf += '*Categories*: %s\n\n' % ', '.join(post['categories'])
    buf += '*Tags*: %s\n\n' % ', '.join(post['tags'])

    buf += '\n\n---\n\n' + post['text'] + '\n\n'

    return buf

def main():
    output = """
---
title: "Computer-Assisted Language Comparison in Practice"
subtitle: "Tutorials on Computational Approaches to the History and Diversity of Languages"
editor: Johann-Mattis List and Tiago Tresoldi
toc-own-page: ture
listings-no-page-break: true
book: true
classoption: oneside
lang: en
titlepage: true
titlepage-color: "2D6CA2"
titlepage-text-color: "FFFFFF"
titlepage-rule-color: "FFFFFF"
titlepage-rule-height: 2
logo: "team-logo.pdf"
logo-width: 250
...

# Introduction

Lorem ipsum, dolor sit amet...
    """
    output += "\n\n"

    for post_idx in POST_IDXS:
        post = {}

        # build url
        print("Processing post #%i..." % post_idx)
        url = 'https://calc.hypotheses.org/%i' % post_idx

        # Obtain the soup object
        req = urllib.request.Request(url, headers=headers)
        raw_html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(raw_html, 'html.parser')

        # Grab the title
        post['title'] = soup.title.string
        post['title'] = post['title'].replace(
            '– Computer-Assisted Language Comparison in Practice', '')
        post['title'].strip()

        # Greb footer material: the first is the author,
        # the date is annotated by a rel='bookmark', then we have categories
        # and tags
        footer_a = soup.footer.find_all('a')
        post['author'] = footer_a[0].string
        post['date_published'] = None
        post['date_updated'] = None
        post['categories'] = []
        post['tags'] = []
        for entry in soup.footer.find_all('a'):
            rels = entry.get('rel')

            if rels:
                if 'bookmark' in rels:
                    times = entry.find_all('time')
                    for time in times:
                        if 'updated' in time.get('class'):
                            post['date_updated'] = time.string
                        else:
                            post['date_published'] = time.string
                elif 'category' in rels:
                    post['categories'].append(entry.string)
                elif 'tag' in rels:
                    if entry.string:
                        post['tags'].append(entry.string)

        # Grab the contents in pandoc
        post_html = soup.find(id='post-%i' % post_idx)
        post['text'] = post2md(post_html.prettify())

        # Append output
        output += build_output(post)

    # Filter all the filenames in the blog, so we can download them
    mapper = {}
    urllib.request.install_opener(opener)
    for image_url in re.findall(r'http.*?png', output):
        # build local filename
        image_path = image_url.replace('/', '_')
        image_path = 'images/' + image_path.split(':', 1)[1]
        mapper[image_url] = image_path

        # download -- need to use the headers...
        print(image_url)
        urllib.request.urlretrieve(image_url, image_path)

    # correct the addresses
    for image_url, image_path in mapper.items():
        output = output.replace(image_url, image_path)

    # correct the CSS styles
    output = output.replace(
        '{style="font-family: terminal, monaco, monospace"}',
        "")

    # add python syntax highlight
    output = output.replace("\n\n```\n", "\n\n```python\n")

    # put the "Cite on" in italics and separate
    output = output.replace(
        "Cite this article as:",
        "**Cite this article as**:")

    # write output to stdin
    with open('calcblog.md', 'w') as handler:
        handler.write(output)

if __name__ == "__main__":
    main()
