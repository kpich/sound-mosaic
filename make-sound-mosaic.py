#import marsyas
import argparse
import os
import subprocess
import time

OUTDIR = 'output'
SAMPLE_RATE = 44100

def optionally_add_output_dir():
    try:
        os.mkdir(OUTDIR)
    except:
        pass

def extract_features(collection, outputid, windowsizems):
    windowSampleSize = (SAMPLE_RATE / 1000) * windowsizems
    subprocess.Popen(['bextract', collection.name,
                      '-w', 'output/' + outputid + '.arff',
                      '-ws', str(windowSampleSize),
                      '-hp', str(windowSampleSize),
                      '-p', '/dev/null']).communicate()
    subprocess.Popen(['kea', '-m', 'distance_matrix',
                      '-dm', 'output/' + outputid + '-matrix.txt',
                     '-w', 'output/' + outputid + '.arff']).communicate()

def match_windows(outputid):
    pass

def create_output_wavfile(outputid):
    pass

def parse_command_line_args():
    '''returns the ArgParser's parsed options.'''
    parser = argparse.ArgumentParser(description='Create a new sound mosaic.')
    parser.add_argument('--collection', type=file, required=True,
                        help='the marsyas collection with labeled source/dest files')
    parser.add_argument('--windowsize', type=int, required=True,
                        help='the window size, in milliseconds')
    parser.add_argument('--output', required=True,
                        help='an identifier for output files')
    return parser.parse_args()

if __name__ == '__main__':
    options = parse_command_line_args()
    print options
    optionally_add_output_dir()
    extract_features(options.collection,
                            options.output,
                            options.windowsize)
    match_windows(options.output)
    create_output_wavfile(options.output)

