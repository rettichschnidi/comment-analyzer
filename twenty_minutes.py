#!/usr/bin/env python3

import argparse
import locale
import re
import sqlite3
import sys
import time

from bs4 import BeautifulSoup
from pip._vendor import requests

URL_COMMENT_BASE = 'http://www.20min.ch/community/storydiscussion/messageoverview.tmpl?storyid='


def error(text, file=sys.stderr):
    print(text, file=file)
    exit(-1)


def parse_comment(soup):
    parent_id = soup.find_parents('li')
    return {
        'comment_id_parent': str(parent_id[0]['id']) if len(parent_id) > 0 else None,
        'comment_id': str(soup['id']),
        'author': str(soup.select('div.entry > div.head > span.author')[0].string),
        'publish_time': time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.strptime(str(soup.select('div.entry > div.head > span.time')[0].string),
                                                    'am %d.%m.%Y %H:%M')),
        'vote_up': int(soup['data-voteup']),
        'vote_down': int(soup['data-votedown']),
        'via_mobile': len(soup.select('div.entry > div.head > span.viamobile')) > 0,
        'title': str(soup.select('div.entry > h3.title')[0].string),
        'content': str(soup.select('div.entry > p.content')[0].string),
    }


def parse_article(soup, url):
    match = re.match('.+-(?P<article_id>\d+$)', url)
    if not match:
        error("Could not extract article id")

    loc = locale.setlocale(locale.LC_TIME, 'de_CH.utf8')
    publish_time = str(soup.select('div#content div.published p')[0].contents[0]).strip()
    date = time.strptime(publish_time, '%d. %B %Y %H:%M;')

    return {
        'id': match.group('article_id'),
        'title': str(soup.find('title').string),
        'url': url,
        'publish_time': time.strftime('%Y-%m-%d %H:%M:%S', date),
    }


def make_soup_from_url(url):
    r = requests.get(url)
    return BeautifulSoup(r.content, 'html.parser')


def analyse_url(story_url):
    conn = sqlite3.connect('twenty_minutes.sqlite3')
    conn.execute('''CREATE TABLE IF NOT EXISTS article
                     (id TEXT PRIMARY KEY,
                      title TEXT NOT NULL,
                      url TEXT NOT NULL,
                      publish_time DATETIME NOT NULL);''')
    conn.execute('''CREATE TABLE IF NOT EXISTS comment
                    (article_id TEXT NOT NULL,
                    comment_id TEXT NOT NULL UNIQUE,
                    comment_id_parent TEXT NULL,
                    author TEXT NOT NULL,
                    publish_time DATETIME NOT NULL,
                    vote_up INTEGER NOT NULL,
                    vote_down INTEGER NOT NULL,
                    via_mobile INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY(article_id) REFERENCES article(id));''')

    article_soup = make_soup_from_url(story_url)
    article = parse_article(article_soup, story_url)
    conn.execute('INSERT OR REPLACE INTO article (id, title, url, publish_time) VALUES (?,?,?,?)',
                 [article['id'], article['title'], article['url'], article['publish_time']])

    comment_soup = make_soup_from_url(URL_COMMENT_BASE + article['id'])
    for soup in [article_soup, comment_soup]:
        for comment_li in soup.select('li.comment'):
            comment = parse_comment(comment_li)
            conn.execute('INSERT OR REPLACE INTO comment VALUES (?,?,?,?,?,?,?,?,?,?)',
                         [article['id'],
                          comment['comment_id'],
                          comment['comment_id_parent'],
                          comment['author'],
                          comment['publish_time'],
                          comment['vote_up'],
                          comment['vote_down'],
                          comment['via_mobile'],
                          comment['title'],
                          comment['content']])
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()
    analyse_url(args.url)


if __name__ == '__main__':
    main()
