#!/usr/bin/env python2.7
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
#

import json
import getopt
import sys
import os
from etllib import compareKeySimilarity, compareValueSimilarity, convertKeyUnicode, generateCluster

_verbose = False
_helpMessage = '''

Usage: clusterscores [-v --verbose] [-h --help] <operation> [--threshold <threshold>] [-f --directory <directory of images>] [-c --file <file1 file2>] 

Operation:
DEFAULT IS -key
--key    
    compare similarity by using file metadata key 

--value
    compare similarity by using file metadata value

Options:  
--threshold [value of threshold] <default threshold = 0.01>
    set threshold for cluster similarity
-o, --output
    the directory of output files
-f, --directory [path to directory]
    read similarity-scores.txt file from this directory
-c, --file [file1 file2]
    compare two given files
-v, --verbose
    Work verbosely rather than silently.
-h --help
    show help on the screen

Example:
clusterscores.py -f [directory of files]                                    
clusterscores.py --threshold 0.001 -f [directory of files]                           
clusterscores.py --value -threshold 0.001 -o [output directory] -f [directory of files]     
clusterscores.py -c [file1 file2]                                         
clusterscores.py --threshold 0.001 -c [file1 file2]                         
clusterscores.py --key --threshold 0.001 -o [output directory] -c [file1 file2] 

'''

def verboseLog(message):
    if _verbose:
        print >>sys.stderr, message

class _Usage(Exception):
    ''' an error for arguments '''

    def __init__(self, msg):
        self.msg = msg

def main(argv = None):
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'f:c:t:o:vhkr', ['directory=', 'file=', 'threshold=', 'output=', 'verbose', 'help', 'key', 'value'])
        except getopt.error, msg:
            raise _Usage(msg)

        if len(opts) ==0:
            raise _Usage(_helpMessage)

        threshold = 0.01
        output_dir = ""
        filenames = []
        filename_list = []
        dirFile = ""
        flag = 1

        for option in argv[1:]:
            if option in ('--key') :
                flag = 1 
            elif option in ('--value') :
                flag = 2 

        if ('-v'in argv) or ('--verbose' in argv):
            global _verbose
            _verbose = True

        elif ('-h'in argv) or ('--help' in argv):
            raise _Usage(_helpMessage) 

        else :
            if ('--threshold' in argv):
                index = argv.index('--threshold')
                threshold = float(argv[index+1])

            if ('-o'in argv) or ('--output' in argv):
                if '-o' in argv :
                    index = argv.index('-o')
                elif '--output' in argv:
                    index = argv.index('--output')
                output_dir = argv[1+index]
                
            if ('-c'in argv) or ('--file' in argv):
                if '-c' in argv:
                    index = argv.index('-c')
                elif '--file' in argv:
                    index = argv.index('--file')
                filenames = argv[1+index : ]
                if len(filenames > 2):
                    raise _Usage("you can only compare two files")

            if('-f' in argv) or ('--directory' in argv) :
                if '-f' in argv:
                    index = argv.index('-f')
                elif '--directory' in argv:
                    index = argv.index('--directory')
                dirFile = argv[index+1]
                filenames=[filename for filename in os.listdir(dirFile) if not filename.startswith('.')]

        #format the filenames
        filenames = [x.strip() for x in filenames]
        filenames = [filenames[k].strip('\'\n') for k in range(len(filenames))]

        for filename in filenames :
            if not os.path.isfile(os.path.join(dirFile, filename)):
                continue
            filename = os.path.join(dirFile, filename) if dirFile else filename
            filename_list.append(filename)

        if len(filename_list) <2 :
            raise _Usage("you need to type in at least two valid files")

        similarity_score = []
        if flag == 1:
            sorted_resemblance_scores, file_parsed_data = compareKeySimilarity(filename_list)
        elif flag ==2:
            sorted_resemblance_scores, file_parsed_data = compareValueSimilarity(filename_list)

        for tuple in sorted_resemblance_scores:
            similarity_score.append(os.path.basename(tuple[0].rstrip(os.sep))+","+str(tuple[1]) + "," + tuple[0] + "," + convertKeyUnicode(file_parsed_data[tuple[0]])+'\n')

        #generate cluster json
        clusterStruct = generateCluster(similarity_score, threshold)
        #output score in file
        with open(os.path.join(output_dir, "clusters.json"), "w") as f:
            f.write(json.dumps(clusterStruct, sort_keys=True, indent=4, separators=(',', ': ')))

    except _Usage, err:
        print >>sys.stderr, sys.argv[0].split('/')[-1] + ': ' + str(err.msg)
        return 2


if __name__ == "__main__":
    sys.exit(main())
