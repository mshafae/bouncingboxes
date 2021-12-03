#!/usr/bin/env python3
import sys
from bb import BBDemo

def main():
    sound_on = not 'soff' in sys.argv
    return BBDemo().run(sound_on)

if __name__ == '__main__':
    main()
