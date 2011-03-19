import marsyas
import optparse
import os
import subprocess

OUTDIR = 'output'
SAMPLE_RATE = 44100

def optionally_add_output_dir():
    try:
        os.mkdir(OUTDIR)
    except:
        pass

def extract_source_features(sourcename, outputid, windowsize):
    call_bextract(sourcename, 'output/' + outputid + '-src.arff', windowsize)

def extract_dest_features(destname, outputid, windowsize):
    call_bextract(destname, 'output/' + outputid + '-dest.arff', windowsize)

def call_bextract(wavfile, outfile, windowSizeInMS):
    windowSampleSize = (SAMPLE_RATE / 1000) * windowSizeInMS
    subprocess.Popen(['bextract', wavfile,
                      '-w', outfile,
                      '-ws', str(windowSampleSize),
                      '-hp', str(windowSampleSize),
                      '-p', '/dev/null']).communicate()

def match_windows(outputid):
    pass

def create_output_wavfile(outputid):
    pass

def parse_command_line_opts():
    '''returns the OptionParser's parsed options.
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
    return parser.parse_args()[0]

if __name__ == '__main__':
    options = parse_command_line_opts()
    optionally_add_output_dir()
    extract_source_features(options.source,
                            options.output,
                            options.windowsize)
    extract_dest_features(options.source,
                          options.output,
                          options.windowsize)
    match_windows(options.output)
    create_output_wavfile(options.output)

