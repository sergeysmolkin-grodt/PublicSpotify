#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для переноса всех треков из Liked Songs в новый публичный плейлист "All tracks"
"""

import os
import sys
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Настройки авторизации
CLIENT_ID = "91b7cd902d2e45c388cfb28e211cef42"
CLIENT_SECRET = "7e12203e067d47888eb0e09d2073a4bf"
REDIRECT_URI = "http://127.0.0.1:8888/callback"  # Убедитесь, что этот URI добавлен в настройках Spotify app
SCOPE = "user-library-read playlist-modify-public"

def main():
    print("Начинаю процесс переноса треков из Liked Songs в публичный плейлист All tracks...")
    
    # Инициализация клиента Spotify с OAuth авторизацией
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE
        ))
        
        # Получаем информацию о текущем пользователе
        user_info = sp.current_user()
        user_id = user_info['id']
        print(f"Авторизован как пользователь: {user_info['display_name']} (ID: {user_id})")
        
        # Создаем новый публичный плейлист
        print("Создаю публичный плейлист 'All tracks'...")
        new_playlist = sp.user_playlist_create(
            user=user_id,
            name="All tracks",
            public=True,
            description="Все мои понравившиеся треки из Liked Songs"
        )
        new_playlist_id = new_playlist['id']
        print(f"Создан новый плейлист 'All tracks' (ID: {new_playlist_id})")
        
        # Получаем все треки из Liked Songs
        print("Получаю список треков из Liked Songs...")
        all_liked_tracks = []
        offset = 0
        limit = 50  # Максимальное количество треков в одном запросе
        
        while True:
            results = sp.current_user_saved_tracks(limit=limit, offset=offset)
            tracks = results['items']
            if not tracks:
                break
                
            all_liked_tracks.extend([track['track']['id'] for track in tracks])
            offset += limit
            
            # Чтобы не превысить лимит запросов API
            if len(tracks) < limit:
                break
                
            # Небольшая пауза, чтобы не перегружать API
            time.sleep(0.5)
        
        print(f"Найдено {len(all_liked_tracks)} треков в Liked Songs")
        
        # Добавляем треки в новый плейлист (максимум 100 за раз)
        print(f"Добавляю треки в плейлист 'All tracks'...")
        
        # Разбиваем список треков на группы по 100 (ограничение API)
        track_chunks = [all_liked_tracks[i:i+100] for i in range(0, len(all_liked_tracks), 100)]
        
        for i, chunk in enumerate(track_chunks):
            sp.playlist_add_items(new_playlist_id, chunk)
            print(f"Добавлено {(i+1) * min(100, len(chunk))}/{len(all_liked_tracks)} треков")
            # Небольшая пауза, чтобы не перегружать API
            time.sleep(1)
        
        print("\nГотово! Все треки из Liked Songs были успешно добавлены в плейлист 'All tracks'")
        print(f"Ссылка на плейлист: https://open.spotify.com/playlist/{new_playlist_id}")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()