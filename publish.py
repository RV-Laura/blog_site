#!/usr/bin/python3
import os, sys, datetime
from bs4 import BeautifulSoup
import re
PRE_HEADER = """

<!DOCTYPE html>
<html>
<meta charset="UTF-8">
<link rel="apple-touch-icon" sizes="180x180" href="images/apple-touch-icon.jpg">
<link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32x32.jpg">
<link rel="icon" type="image/png" sizes="16x16" href="images/favicon-16x16.jpg">
<style>
@media (prefers-color-scheme: dark) {
    body {
        background-color: #1c1c1c;
        color: white;
    }
    .markdown-body table tr {
        background-color: #1c1c1c;
    }
    .markdown-body table tr:nth-child(2n) {
        background-color: black;
    }
}
::selection{
  background:#828c96;
  color:#fff;
}

.monospace{
  font-family:NBInter,monospace;
  line-height:1.75;
}

.m0{
  margin:0!important;
}

.cssP{
    line-height: 1.59;
    margin-bottom: 2.4rem;
    font-weight: 400;
    font-family: RiformaLLSub,helvetica Neue,Helvetica,arial,sans-serif;
    color:#828c96;
}

.settingsP{
  font-weight:400;
  display: block;
  margin-block-start: 1em;
  margin-block-end: 1em;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
}

.ulLista{
  line-height: 1.59;
  font-weight: 400;
  font-family: RiformaLLSub,helvetica Neue,Helvetica,arial,sans-serif;
  padding:0;
  display: block;
  list-style-type: disc;
  margin-block-start: 1em;
  margin-block-end: 1em;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
  padding-inline-start: 0px;
  width :auto;
  line-height:250%;
}

.buttonList{
  display: inline-block;
  margin-right:0.7rem;
}

.p0{
  padding:0!important;
}

.settingsli{
  margin:0;
  margin-bottom:0;
  line-height:1.59;
  font-weight: 400;
  font-family: RiformaLLSub,helvetica Neue,Helvetica,arial,sans-serif;
}
.button{
  background: #dce6f0;
  color: #19232d;
  padding: 0.35rem 0.9rem;
  font-family: NBInter,monospace;
  text-decoration: none!important;
  border-radius: 0.4rem;
  transition:color .25s,background .25s,opacity .25s;
  cursor:pointer;
}
.button:hover{
  background:#19232d;
  color:#fff;
}
#ez-toc-container ul{
        font-family:NBInter,monospace;
        counter-reset:line;
}
#ez-toc-container #line{
        display:block;
        counter-increment:line;
}
#ez-toc-container #line::before{
        display:inline-block;
        width:0.05px;
        padding-right:0.5em;
        margin-right:0.8em;
        content: counter(line);
}
#noSpace{
        padding:0;
} 
html{
        scroll-behavior:smooth;
}

</style>

"""

HEADER_TEMPLATE = """

<link rel="stylesheet" type="text/css" href="$root/css/common-vendor.b8ecfc406ac0b5f77a26.css">
<link rel="stylesheet" type="text/css" href="$root/css/fretboard.f32f2a8d5293869f0195.css">
<link rel="stylesheet" type="text/css" href="$root/css/pretty.0ae3265014f89d9850bf.css">
<link rel="stylesheet" type="text/css" href="$root/css/pretty-vendor.83ac49e057c3eac4fce3.css">
<link rel="stylesheet" type="text/css" href="$root/css/misc.css">


<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script type="text/javascript" id="MathJax-script" async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
</script>

<style>
</style>

<div id="doc" class="container-fluid markdown-body comment-enabled" data-hard-breaks="true">

"""

RSS_LINK = """

<link rel="alternate" type="application/rss+xml" href="{}/feed.xml" title="{}">

"""

TITLE_TEMPLATE = """

<br>
<h1 style="margin-bottom:7px"> {0} </h1>
<small style="float:left; color: #888"> {1} </small>
<small style="float:right; color: #888"><a href="{2}/index.html">See all posts</a></small>
<br> <br> <br>
<title> {0} </title>

"""

TOC_TITLE_TEMPLATE = """

<title> {0} </title>
<br>
<center><h1 style="border-bottom:0px"> {0} </h1></center>

"""

FOOTER = """
 </div>

<script>
	// remove fragment as much as it can go without adding an entry in browser history:
window.location.replace("#");

// slice off the remaining '#' in HTML5:    
if (typeof window.history.replaceState == 'function') {
  history.replaceState({}, '', window.location.href.slice(0, -1));
}
	

</script>
"""

TOC_START = """

<br>
<ul class="post-list" style="padding-left:0">

"""

TOC_END = """ </ul> """

TOC_ITEM_TEMPLATE = """

<li>
    <span class="post-meta">{}</span>
    <h3 style="margin-top:12px">
      <a class="post-link" href="{}">{}</a>
    </h3>
</li>

"""

TWITTER_CARD_TEMPLATE = """
<meta name="twitter:card" content="summary" />
<meta name="twitter:title" content="{}" />
<meta name="twitter:image" content="{}" />
"""


RSS_ITEM_TEMPLATE = """
<item>
<title>{title}</title>
<link>{link}</link>
<guid>{link}</guid>
<pubDate>{pub_date}</pubDate>
<description>{description}</description>
</item>
"""


RSS_MAIN_TEMPLATE = """
<?xml version="1.0" ?>
<rss version="2.0">
<channel>
  <title>{title}</title>
  <link>{link}</link>
  <description>{title}</description>
  <image>
      <url>{icon}</url>
      <title>{title}</title>
      <link>{link}</link>
  </image>
{items}
</channel>
</rss>
"""
CONTENT_INICIO = """
<div id="ez-toc-container">
	<div>
		<p>Contents</p>
		<br>
	</div>
	<nav>
		<ul id="noSpace">


"""

CONTENT_FIN= """
</ul>
	</nav>

</div>
"""
def extract_metadata(fil, filename=None):
    metadata = {}
    if filename:
        assert filename[-3:] == '.md'
        metadata["filename"] = filename[:-3]+'.html'
    while 1:
        line = fil.readline()
        if line and line[0] == '[' and ']' in line:
            key = line[1:line.find(']')]
            value_start = line.find('(')+1
            value_end = line.rfind(')')
            if key in ('category', 'categories'):
                metadata['categories'] = set([
                    x.strip().lower() for x in line[value_start:value_end].split(',')
                ])
                assert '' not in metadata['categories']
            else:
                metadata[key] = line[value_start:value_end]
        else:
            break
    return metadata


def metadata_to_path(global_config, metadata):
    return os.path.join(
        global_config.get('posts_directory', 'posts'),
        metadata['date'],
        metadata['filename']
    )


def generate_feed(global_config, metadatas):
    def get_link(route):
        return global_config['domain'] + "/" + route

    def get_date(date_text):
        year, month, day = (int(x) for x in date_text.split('/'))
        date = datetime.date(year, month, day)
        return date.strftime('%a, %d %b %Y 00:00:00 +0000')

    def get_item(metadata):
        return RSS_ITEM_TEMPLATE.format(
            title=metadata['title'],
            link=get_link('/'.join([global_config['posts_directory'], metadata['date'], metadata['filename']])),
            pub_date=get_date(metadata['date']), description=''
        )

    return RSS_MAIN_TEMPLATE.strip().format(
        title=global_config['title'],
        link=get_link(''),
        icon=global_config['icon'],
        items="\n".join(map(get_item, metadatas))
    )




def make_twitter_card(title, global_config):
    return TWITTER_CARD_TEMPLATE.format(title, global_config['icon'])


def defancify(text):
    return text \
        .replace("’", "'") \
        .replace('“', '"') \
        .replace('”', '"') \
        .replace('…', '...') \


def make_categories_header(categories, root_path):
    o = ['<div><br><div><p class="cssP" >Collected writing and research by ilyass</p></div></div><div class="m0 ulLista"><hr><p class="monospace m0 settingsP">Filter</p>']
    for category in categories:
        template = '<span class="buttonList noBullets settingsLi" style="font-size:{}%"><a class="button button--active" href="{}/categories/{}.html">{}</a></span>'
        o.append(template.format(min(100, 1000 // len(category)), root_path, category, category.capitalize()))
    o.append('<hr></div>')
    return '\n'.join(o)


def get_printed_date(metadata):
    year, month, day = metadata['date'].split('/')
    month = 'JanFebMarAprMayJunJulAugSepOctNovDec'[int(month)*3-3:][:3]
    return year + ' ' + month + ' ' + day

def make_toc_item(global_config, metadata, root_path):
    link = metadata_to_path(global_config, metadata)
    return TOC_ITEM_TEMPLATE.format(get_printed_date(metadata), root_path + '/' + link, metadata['title'])


def make_toc(toc_items, global_config, all_categories, category=None):
    if category:
        title = category.capitalize()
        root_path = '..'
    else:
        title = global_config['title']
        root_path = '.'

    return (
        PRE_HEADER +
        RSS_LINK.format(root_path, title) +
        HEADER_TEMPLATE.replace('$root', root_path) +
        make_twitter_card(title, global_config) +
        TOC_TITLE_TEMPLATE.format(title) +
        make_categories_header(all_categories, root_path) +
        TOC_START +
        ''.join(toc_items) +
        TOC_END
    )


if __name__ == '__main__':
    # Get blog config
    global_config = extract_metadata(open('config.md'))

    # Special case: '--sync' option
    if '--sync' in sys.argv:
        os.system('rsync -av site/. {}:{}'.format(global_config['server'], global_config['website_root']))
        sys.exit()

    # Normal case: process each provided file
    for file_location in sys.argv[1:]:
        filename = os.path.split(file_location)[1]
        print("Processing file: {}".format(filename))
        
        # Extract path
        file_data = open(file_location).read()
        metadata = extract_metadata(open(file_location), filename)
        path = metadata_to_path(global_config, metadata)

        # Generate the html file
        options = metadata.get('pandoc', '')
        
        os.system('pandoc -o /tmp/temp_output.html {} {}'.format(file_location, options))
        root_path = '../../../..'
        with open('/tmp/temp_output.html') as f:
            #read File
            content = f.read()
            #parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            o = []
            childs = []
            count =0
            flag = False
	    #Partimos con la idea de que en nuestro doc siempre empezamos con h2 despues del h1 del titulo
            for link in soup.find_all(re.compile('^h[1-6]$')):
                if link.name == 'h3':
                    flag = True
                else:
                    flag = False
                    count = count+1
                if flag:
                    template2='<li id="line" class="{}"><a href="{}">{}</a></li>'
                    childs.append(template2.format(count,"#"+link.get('id'),link.string))
                else:
                    template = '<li id="line" class="{}"><a href="{}">{}</a></li>'
                    o.append(template.format(count,"#"+link.get('id'),link.string))
            
            test='\n'.join(o)
            testChilds='\n'.join(childs)
            #print(test)
            #print('---------')
            #print(testChilds)
            #print(' ')
            #pasamos los resultados obtenidos a una string
         
        soup = BeautifulSoup(test, 'html.parser')
        soupC = BeautifulSoup(testChilds, 'html.parser')
        cajita=[]
        result=[]
        flag = False
        #Partimos con la idea de que en nuestro doc siempre empezamos con h2 despues del h1 del titulo
        for padre in soup.find_all('li'): 
            for hijo in soupC.find_all('li'):
                if padre.get('class') == hijo.get('class'):
                    flag = True
                    for link in hijo.find_all('a'):
                        templateF = '<li id="line" class="{}"><a href="{}">{}</a></li>'
                        cajita.append(templateF.format(count,link.get('href'),hijo.string))
            if flag:
                for link in padre.find_all('a'):
                    templateFlag = '<li id="line" class="{}"><a href="{}">{}</a><ul>{}</ul></li>'
                    test=' '.join(cajita)
                    result.append(templateFlag.format(count,link.get('href'),padre.string,test))
            else:
                for link in padre.find_all('a'):
                    templateF = '<li id="line" class="{}"><a href="{}">{}</a></li>'
                    result.append(templateF.format(count,link.get('href'),padre.string))
            flag=False
            cajita=[]
        resultado='\n'.join(result)
        #print(resultado)



        total_file_contents = (
            PRE_HEADER +
            RSS_LINK.format(root_path, metadata['title']) +
            HEADER_TEMPLATE.replace('$root', root_path) +
            make_twitter_card(metadata['title'], global_config) +
            TITLE_TEMPLATE.format(metadata['title'], get_printed_date(metadata), root_path) +
            CONTENT_INICIO +
            resultado +
            CONTENT_FIN+
            defancify(open('/tmp/temp_output.html').read()) +
            FOOTER
        )

        print("Path selected: {}".format(path))
        
        # Make sure target directory exists
        truncated_path = os.path.split(path)[0]
        os.system('mkdir -p {}'.format(os.path.join('site', truncated_path)))
        
        # Put it in the desired location
        out_location = os.path.join('site', path)
        open(out_location, 'w').write(total_file_contents)

    # Reset ToC
    metadatas = []
    categories = set()
    for filename in os.listdir('posts'):
        if filename[-4:-1] != '.sw':
            metadatas.append(extract_metadata(open(os.path.join('posts', filename)), filename))
            categories = categories.union(metadatas[-1]['categories'])
            
    print("Detected categories: {}".format(' '.join(categories)))

    sorted_metadatas = sorted(metadatas, key=lambda x: x['date'], reverse=True)
    feed = generate_feed(global_config, sorted_metadatas)

    os.system('mkdir -p {}'.format(os.path.join('site', 'categories')))

    print("Building tables of contents...")

    homepage_toc_items = [
        make_toc_item(global_config, metadata, '.') for metadata in sorted_metadatas if
        global_config.get('homepage_category', '') in metadata['categories'].union({''})
    ]

    for category in categories:
        category_toc_items = [
            make_toc_item(global_config, metadata, '..') for metadata in sorted_metadatas if
            category in metadata['categories']
        ]
        toc = make_toc(category_toc_items, global_config, categories, category)
        open(os.path.join('site', 'categories', category+'.html'), 'w').write(toc)

    open('site/feed.xml', 'w').write(feed)
    open('site/index.html', 'w').write(make_toc(homepage_toc_items, global_config, categories))

    # Copy CSS and scripts files
    this_file_directory = os.path.dirname(__file__)
    os.system('cp -r {} site/'.format(os.path.join(this_file_directory, 'css')))
    os.system('cp -r {} site/'.format(os.path.join(this_file_directory, 'scripts')))
    os.system('rsync -av images site/')
