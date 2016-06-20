# -*- coding: utf-8 -*-
"""
Displays the current Song in Google Play Music Desktop Player.

Configuration parameters:
    format_play: text format if a song is playing
    format_pause: text format if a song is paused
    format_stop: text format if the player stopped
    path: Path to the Playback-Api of GPMDP
    color_play: color for status play
    color_pause: color for status paused
    color_stop: color for status stopped
    cache_timeout: time of refreshes
    text_pause: Text for paused player
    text_stop: Text for stopped player
    icon: general icon
    icon_(play|pause|stop): specific icon for mode

    Default configuration:
    format_play: '{icon} {title} {album}/{artist} ({percentage})'
    format_pause: '{icon} {text}'
    format_stop: '{icon} {text}'
    path: '~/.config/Google Play Music Desktop Player/json_store/playback.json'
    cache_timeout: 10
    text_pause: Player paused
    text_stop: Player stopped
    color: play = good, pause = degraded, stop = bad
    icon: u'\u266B'

    Possible Text Tags:
    {title}
    {artist}
    {album}
    {liked}
    {current_time}
    {total_time}
    {percentage}
    {icon}
    {text}
@author ChrisB9
"""

import os
import json
from time import time
from datetime import timedelta


class Song:
    title = None
    artist = None
    album = None
    liked = None
    current_time = None
    total_time = None
    percentage = None
    playing = None


class Py3status:
    """
    """
    # configuration parameters
    format_play = '{icon} {title} {album}/{artist} ({percentage})'
    format_pause = '{icon} {text}'
    format_stop = '{icon} {text}'
    path = '~/.config/Google Play Music Desktop Player/json_store/playback.json'
    color_play = None
    color_pause = None
    color_stop = None
    cache_timeout = 10
    text_pause = None
    text_stop = None
    icon = u'\u266B'
    icon_play = u'\u266B'
    icon_stop = u'\u266B'
    icon_pause = u'\u266B'
    cached_song = None

    def print_method(self, i3s_output_list, i3s_config):
        response = {
            'cached_until': time() + self.cache_timeout
        }
        playmusic_data = self._get_play_music_json()

        if not playmusic_data.title:
            response['full_text'] = self.format_stop.format(
                text=self.text_stop or 'Player stopped',
                icon=self.icon_stop.encode('utf-8') or self.icon.encode('utf-8')
            )
            response['color'] = self.color_stop or i3s_config['color_bad']
        else:
            if playmusic_data.playing:
                response['full_text'] = self.format_play.format(
                    title=playmusic_data.title,
                    artist=playmusic_data.artist,
                    album=playmusic_data.album,
                    current=playmusic_data.current_time,
                    total=playmusic_data.total_time,
                    percentage=playmusic_data.percentage,
                    liked=playmusic_data.liked,
                    icon=self.icon_play.encode('utf-8') or self.icon.encode('utf-8')
                )
                response['color'] = self.color_play or i3s_config['color_good']
            else:
                response['full_text'] = self.format_pause.format(
                    text=self.text_pause or 'Player paused',
                    icon=self.icon_pause.encode('utf-8') or self.icon.encode('utf-8')
                )
                response['color'] = self.color_pause or i3s_config['color_degraded']
        return response

    def _get_play_music_json(self):
        json_file = open(os.path.expanduser(self.path), "r")
        try:
            data = json.load(json_file)
            song = Song()
            song.title = data['song']['title']
            song.current_time = data['time']['current']
            song.total_time = data['time']['total']
            song.title = data['song']['title']
            song.artist = data['song']['artist']
            song.playing = data['playing']
            if not data['rating']['liked']:
                if not data['rating']['disliked']:
                    song.liked = None
                else:
                    song.liked = False
            else:
                song.liked = True
            song.album = data['song']['album']
            song.percentage = str(
                round(
                    self._get_song_duration_percentage(
                        song.current_time, song.total_time),
                    2)
                ) + "%"
            song.current_time = str(timedelta(microseconds=song.current_time))[:-7]
            song.total_time = str(timedelta(microseconds=song.total_time))[:-7]
            self.cached_song = song
            return song
        except ValueError:
            return self.cached_song

    def _turn_ms_to_min(ms):
        return round(float(ms) / float(60000), 2)

    def _get_song_duration_percentage(self, current, total):
        try:
            current = float(current)
            total = float(total)
        except ValueError:
            return 0.0
        if (current * total) == 0:
            return 0.0
        return float(current) / float(total) * 100

if __name__ == "__main__":
    """
    Module testing
    """
    from time import sleep
    playmusic = Py3status()
    config = {
        'color_bad': '#FF0000',
        'color_degraded': '#FFFF00',
        'color_good': '#00FF00'
    }
    count = 0
    while count < 10:
        count += 1
        print(playmusic.print_method([], config))
        sleep(1)
