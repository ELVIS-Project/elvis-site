import os
from music21 import *
import sys
from correcting_MEI_files import modifying_MEI
from validating_MEI_files import validation


def convert_MEI_into_midi(meipath):
    """
    Convert the corrected MEI files into midi, so that jsymbolic2 can process all MEI files and extract features
    :return:
    """
    if os.path.exists(meipath + 'MIDI/') is False:
        os.mkdir(meipath + 'MIDI/')
    flog = open(meipath + 'MEI_to_midi_log.txt', 'w')
    for id, fn in enumerate(os.listdir(meipath)):
        if (fn[-3:] != 'mei'):
            continue  # only convert xml into midi
        print(fn)
        try:
            s = converter.parse(meipath + fn)
            s.write('midi', fp = meipath +'MIDI/' + fn + '.midi')
        #s.write('xml', fp='./downloaded_files/MEI/NEW/MIDI/' + fn + '.xml')
        except:
            print(fn, file=flog)
            print(sys.exc_info()[0], file=flog)
def convert_xml_into_midi():
    if os.path.exists('./downloaded_files/XML/MIDI/') is False:
        os.mkdir('./downloaded_files/XML/MIDI/')
    flog = open('./downloaded_files/XML/MIDI/xml_to_midi_log.txt', 'w')
    for id, fn in enumerate(os.listdir('./downloaded_files/XML/')):
        if (fn[-3:] != 'xml'):
            continue  # only convert xml into midi
        print(fn)
        try:
            s = converter.parse('./downloaded_files/XML/' + fn)
            s.write('midi', fp = './downloaded_files/XML/MIDI/' + fn + '.midi')
        except:
            print(fn, file=flog)
            print(sys.exc_info()[0], file=flog)


def extract_features_per_folder(filepath, featurepath, path):
    """
    Create the folder for the features, and then extract features and store them
    :param filepath: original file path
    :param featurepath: directory for the features to store
    :param path: path to store jsymbolic2 jar file
    :return:
    """
    if os.path.exists(featurepath) is False:
        os.mkdir(featurepath)
    for id, fn in enumerate(os.listdir(filepath)):  # extract features for all the original midi files
        print(fn)
        os.system('java -Xmx8192m -jar ' + path + ' -configrun jSymbolicDefaultConfigs.txt ' + filepath +  fn + ' ' +
                  featurepath + fn + '_feature_values.xml ' +
                    featurepath + fn + '_feature_descriptions.xml >>' + featurepath + 'extract_features_log.txt 2'
                    '>>' + featurepath + 'extract_features_error_log.txt')


def extract_features(path):
    extract_features_per_folder('./downloaded_files/', './downloaded_files/extracted_features/', path)
    extract_features_per_folder('./downloaded_files/MEI/NEW/', './downloaded_files/MEI/NEW/extracted_features/', path)
    extract_features_per_folder('./downloaded_files/XML/MIDI/', './downloaded_files/XML/MIDI/extracted_features/', path)
    extract_features_per_folder('./downloaded_files/MEI/NEW/MIDI/', './downloaded_files/MEI/NEW/MIDI/extracted_features/',
                                path)


if __name__ == "__main__":
    #jsymbolic_path = input('please specify jsymbolic path')
    jsymbolic_path = './jMIR_3_0_developer/jSymbolic2/dist/jSymbolic2.jar'
    rng_path = rng_path = ['./MEI_schemata_files/mei-all-3.0.0.rng', './MEI_schemata_files/mei-all-2013.rng', './MEI_schemata_files/MEI2010-05.rng', './MEI_schemata_files/MEI2011-05.rng']
    mei_path = './downloaded_files/MEI/NEW/'
    #mei_path = './downloaded_files_2/'
    convert_xml_into_midi()
    modifying_MEI()
    #validation(rng_path[3], mei_path)
    convert_MEI_into_midi(mei_path)
    extract_features(jsymbolic_path)