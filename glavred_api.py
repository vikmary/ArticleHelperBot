#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import math
import requests


class GlavRed:

    WORDS = re.compile('([А-Яа-яA-Za-z0-9-]+([^А-Яа-яA-Za-z0-9-]+)?)')

    def __init__(self):
        self.sess = None
        self.url = "https://glvrd.ru/api/v0/"
        self.headers = \
                {"Content-Type": "application/x-www-form-urlencoded"}

    def __enter__(self):
        self.sess = requests.Session()
        return self

    def __exit__(self, *args):
        self.sess.close()

    def get_score(self, texts, score_type):
        texts_and_frams = []

        for t in texts:
            res = self.proofread(t, score_type)
            fragments, hints = res['fragments'][0], res['hints']
            for i in range(len(fragments)):
                hint_id = fragments[i]['hint']
                fragments[i]['hint'] = hints[hint_id]

            t_f = {'text': t,
                   'fragments': fragments}
            texts_and_frams.append(t_f)

        return self._get_score(texts_and_frams)

    def proofread(self, text, score_type):
        assert score_type in ('red', 'blue')
        resp = self.sess.post('{}@proofread/{}/'.format(self.url,
                                                        score_type),
                              headers=self.headers,
                              data={'chunks': text})
        if resp.status_code != 200:
            raise Exception("Status code `{}` received for chunks=`{}`"\
                            .format(resp.status_code, text))
        return resp.json()

    def _get_score(self, texts_and_frams):
        n, r, t = 0, 0, 0
        for t_f in texts_and_frams:
            t += self.num_words(t_f['text'])
            for f in t_f['fragments']:
                if f['hint']['penalty']:
                    n += f['hint']['penalty']
                r += f['hint']['weight'] / 100
        if not t:
            return 0.
        score = math.floor(100. * math.pow(1 - r / t, 3)) - n
        #print("n = {}, r = {}, t = {}".format(n, r, t))
        score = min(max(score, 0.), 100.)
        if score % 10 == 0:
            return score / 10
        else:
            return round(score / 10, 1)

    @classmethod
    def num_words(cls, text):
        return len(cls.WORDS.sub('.', text.strip()))


