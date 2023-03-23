# qt_slideshow

This is a very simple python program that uses QT to display images on a screen. It was mostly written by ChatGPT4 as I've never used QT before.

This version uses pyside6 but it appears to work just fine with pyside2 or PyQt*. I did see a crash using PyQt6 when running images at speed = 0. 

It uses two timers. One to show an image and the other to show the word "Paused" when paused.

See keypress for support keyboard commands. 
