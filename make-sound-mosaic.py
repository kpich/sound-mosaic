import argparse
import os
import subprocess

OUTDIR = 'output/'
SAMPLE_RATE = 44100
SRC_LABEL = 'source'
DEST_LABEL = 'dest'

def optionally_add_output_dir():
    try:
        os.mkdir(OUTDIR)
    except:
        pass

def make_arff_filename(outputid):
    return OUTDIR + outputid + '.arff'

def make_dm_filename(outputid):
    return OUTDIR + outputid + '-matrix.txt'

def extract_features(collection, outputid, windowsizems):
    windowSampleSize = (SAMPLE_RATE / 1000) * windowsizems
    subprocess.Popen(['bextract', collection.name,
                      '-w', make_arff_filename(outputid),
                      '-ws', str(windowSampleSize),
                      '-hp', str(windowSampleSize),
                      '-p', '/dev/null']).communicate()
    subprocess.Popen(['kea', '-m', 'distance_matrix',
                      '-dm', make_dm_filename(outputid),
                     '-w', make_arff_filename(outputid)]).communicate()

def match_windows(outputid):
    ''' For each dest window, finds the closes source window.

    NOTE it is very important that in the input .mf file, the source files
    all appear together, before the dest files.
    '''
    srclen, destlen = get_source_dest_window_counts(outputid)
    print srclen
    print destlen

def get_source_dest_window_counts(outputid):
    lines = open(make_arff_filename(outputid), 'r').readlines()
    return len(filter(is_src_line, lines)), len(filter(is_dest_line, lines))

def is_src_line(line):
    return line.strip().endswith(',' + SRC_LABEL)

def is_dest_line(line):
    return line.strip().endswith(',' + DEST_LABEL)

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

