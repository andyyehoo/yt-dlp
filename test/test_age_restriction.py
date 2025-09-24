#!/usr/bin/env python3

# Allow direct execution
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from test.helper import is_download_test, try_rm
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def _is_expected_error(err):
    return err.exc_info and getattr(err.exc_info[1], 'expected', False)


def _download_restricted(url, filename, age):
    """Attempt to download ``url`` while respecting ``age`` restrictions."""

    params = {
        'age_limit': age,
        'skip_download': True,
        'writeinfojson': True,
        'outtmpl': '%(id)s.%(ext)s',
    }
    ydl = YoutubeDL(params)
    ydl.add_default_info_extractors()
    json_filename = os.path.splitext(filename)[0] + '.info.json'
    try_rm(json_filename)
    downloaded = False
    try:
        ydl.download([url])
        downloaded = os.path.exists(json_filename)
    finally:
        try_rm(json_filename)
    return downloaded


@is_download_test
class TestAgeRestriction(unittest.TestCase):
    def _assert_restricted(self, url, filename, age, old_age=None):
        try:
            can_download = _download_restricted(url, filename, old_age)
        except DownloadError as err:
            if _is_expected_error(err):
                self.fail(f'Expected unrestricted download but got: {err}')
            self.skipTest(f'Download failed: {err}')
        else:
            self.assertTrue(can_download)

        try:
            restricted = _download_restricted(url, filename, age)
        except DownloadError as err:
            if _is_expected_error(err):
                return
            self.skipTest(f'Download failed: {err}')
        else:
            self.assertFalse(restricted)

    def test_youtube(self):
        self._assert_restricted('HtVdAasjOgU', 'HtVdAasjOgU.mp4', 10)

    def test_youporn(self):
        self._assert_restricted(
            'https://www.youporn.com/watch/16715086/sex-ed-in-detention-18-asmr/',
            '16715086.mp4', 2, old_age=25)


if __name__ == '__main__':
    unittest.main()
