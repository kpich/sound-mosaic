import marsyas
import optparse
import subprocess
import sys

def extract_feature_windows(files):
    for f in files:
        subprocess.Popen(['bextract', f,
                          '-w', 'features-' + f + '.arff',
                          '-p', '/dev/null'])

def parse_command_line_opts()
    '''returns the OptionParser.
        We're stuck with python26 so can't use an argparser!
    '''
    parser = optparse.OptionParser(description='Create a new sound mosaic.')
    parser.add_option('--source', type='string',
                        help='the source wavfile to cut up')
    parser.add_option('--dest', type='string',
                        help='the destionation wavfile to try to recreate')
    parser.add_option('--windowsize', type='int',
                        help='the window size, in milliseconds')
    parser.add_option('--output', type='string',
                        help='an identifier for output files')
    return parser

if __name__ == '__main__':
    parse_command_line_opts()
    extract_source_features()
    extract_dest_features()
    match_windows()
    create_output_wavfile()

