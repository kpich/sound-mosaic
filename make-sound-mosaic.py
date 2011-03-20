import argparse
import itertools
import os
import re
import subprocess

OUTDIR = 'output/'
TMPDIR = 'output/tmp/'
SAMPLE_RATE = 44100
SRC_LABEL = 'source'
DEST_LABEL = 'dest'

def optionally_add_output_dir():
    try: os.mkdir(OUTDIR)
    except: pass
    try: os.mkdir(TMPDIR)
    except: pass

def make_arff_filename(outputid):
    return OUTDIR + outputid + '.arff'

def make_dm_filename(outputid):
    return OUTDIR + outputid + '-matrix.txt'

def make_mf_filename(outputid):
    return TMPDIR + outputid + '.mf'

def make_tmp_window_wavfilename(windownum, outputid):
    return TMPDIR + outputid + "_" + str(windownum) + ".wav"

def make_mf_file(srcfile, destfile, outputid):
    f = open(make_mf_filename(outputid), 'w')
    f.write(srcfile.name + '\t' + SRC_LABEL + '\n')
    f.write(destfile.name + '\t' + DEST_LABEL + '\n')
    f.close()

def extract_features(srcfile, destfile, outputid, windowsizems):
    windowSampleSize = (SAMPLE_RATE / 1000) * windowsizems
    make_mf_file(srcfile, destfile, outputid)
    subprocess.Popen(['bextract', make_mf_filename(outputid),
                      '-w', make_arff_filename(outputid),
                      '-mfcc',
                      '-ws', str(windowSampleSize),
                      '-hp', str(windowSampleSize),
                      '-m', '1',
                      '-fe']).communicate()
    subprocess.Popen(['kea', '-m', 'distance_matrix',
                      '-dm', make_dm_filename(outputid),
                      '-w', make_arff_filename(outputid)]).communicate()

def match_windows(outputid):
    ''' For each dest window, finds the closes source window.

    NOTE it is very important that in the input .mf file, the source files
    all appear together, before the dest files.
    '''
    srclen, destlen = get_source_dest_window_counts(outputid)
    dists = get_src_dest_dists(outputid, srclen, destlen)
    return [argmin(x) for x in dists]

def argmin(li):
    '''cribbed from http://lemire.me/blog/archives/2004/11/25/computing-argmax-fast-in-python/'''
    return min(itertools.izip(li, xrange(len(li))))[1]

def get_src_dest_dists(outputid, srclen, destlen):
    '''returns a destlen-elem list of srclen-elem lists: all relevant distances.
    '''
    dists = [[-1.0 for x in range(srclen)] for y in range(destlen)]
    firstdestind = srclen
    for line in open(make_dm_filename(outputid), 'r'):
        if is_interesting_line(line, firstdestind):
            add_dist_to_dists(line, dists, firstdestind)
    #make sure our lists are fully populated
    for li in dists:
        assert -1.0 not in li
    return dists

def is_interesting_line(line, firstdestind):
    m = re.match(r'\((\d+),(\d+)\)', line)
    return (m and 
           int(m.group(1)) < firstdestind and
           int(m.group(2)) >= firstdestind)

def add_dist_to_dists(line, dists, firstdestind):
    m = re.match(r'\((\d+),(\d+)\)\s*=\s*([0-9.]+)', line)
    assert m
    i = int(m.group(1))
    j = int(m.group(2))
    d = float(m.group(3))
    dists[j - firstdestind][i] = d

def get_source_dest_window_counts(outputid):
    lines = open(make_arff_filename(outputid), 'r').readlines()
    return len(filter(is_src_line, lines)), len(filter(is_dest_line, lines))

def is_src_line(line):
    return line.strip().endswith(',' + SRC_LABEL)

def is_dest_line(line):
    return line.strip().endswith(',' + DEST_LABEL)

def create_output_wavfile(srcfile, destfile, windowmatches, outputid, windowsizems):
    windowsizesamples = (SAMPLE_RATE / 1000) * windowsizems
    make_src_snippets_in_tmp(srcfile, windowmatches, outputid, windowsizesamples)

def make_src_snippets_in_tmp(srcfile, windowmatches, outputid, windowsizesamples):
    for m in windowmatches:
        subprocess.Popen(['sox',
                          srcfile.name,
                          make_tmp_window_wavfilename(m, outputid),
                          'trim',
                          str(m * windowsizesamples) + 's',
                          str(windowsizesamples) + 's']).communicate()

def parse_command_line_args():
    '''returns the ArgParser's parsed options.'''
    parser = argparse.ArgumentParser(description='Create a new sound mosaic.')
    parser.add_argument('--src', type=file, required=True,
                        help='the source wavfile')
    parser.add_argument('--dest', type=file, required=True,
                        help='the destination wavfile')
    parser.add_argument('--windowsize', type=int, required=True,
                        help='the window size, in milliseconds')
    parser.add_argument('--output', required=True,
                        help='an identifier for output files')
    return parser.parse_args()

if __name__ == '__main__':
    options = parse_command_line_args()
    print options
    optionally_add_output_dir()
    extract_features(options.src,
                     options.dest,
                     options.output,
                     options.windowsize)
    windowmatches = match_windows(options.output)
    create_output_wavfile(options.src,
                          options.dest,
                          windowmatches,
                          options.output,
                          options.windowsize)

