#!/usr/bin/env bash
# KDE retains its native authentication and secure locker.
exec qdbus6 org.freedesktop.ScreenSaver /ScreenSaver org.freedesktop.ScreenSaver.Lock
