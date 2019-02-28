# encoding: utf-8

import re
import urllib.request
from bs4 import BeautifulSoup
import pypandoc

headers = {}
headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0"

POST_IDXS = [
    22, # Mattis, Let the Games Begin
    32, # Tiago, Wiktionary
    58, # Mattis, Exporting sublists
    384, # Mattis, CLICS
    445, # Mattis, CLDF
    477, # Mattis, consonant class matching
    570, # Nathanael, annotation
    998, # Mattis, consonant clusters
    803, # Gereon, fieldwork 1
    1169, # Nathanael, promiscuity
    849, # Gereon, Fieldwork 2
    1668, # Mattis, merging datasets

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
    buf = "## %s\n\n(%s -- %s - %s)\n\n" % \
        (post['title'], post['author'], post['date_published'], post['date_updated'])
    buf += 'Categories: %s\n\n' % ', '.join(post['categories'])
    buf += 'Tags: %s\n\n' % ', '.join(post['tags'])

    buf += '\n\n' + post['text']

    return buf

def main():
    output = "# CALC Blog 2018\n\n"

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
                else:
                    post['tags'].append(entry.string)

        # Grab the contents in pandoc
        post_html = soup.find(id='post-%i' % post_idx)
        post['text'] = post2md(post_html.prettify())

        # Append output
        output += build_output(post)

    # write output to stdin
    with open('output.md', 'w') as handler:
        handler.write(output)

if __name__ == "__main__":
    main()
