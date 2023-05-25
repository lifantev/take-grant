import getopt
import sys
from take_grant import *


def main(argv):
    help_msg = 'can_share.py -f <filename_of_protection_graph.json> -s <source_object> -d <destination_object> -a <rule_label>'

    src = ''
    dst = ''
    a = ''
    filename = ''
    opts, _ = getopt.getopt(argv, "hf:s:d:a:")
    for opt, arg in opts:
        if opt == '-h':
            print(help_msg)
            sys.exit()
        elif opt == '-f':
            filename = arg
        elif opt == '-s':
            src = arg
        elif opt == '-d':
            dst = arg
        elif opt == '-a':
            a = arg

    if filename == '' or src == '' or dst == '' or a == '':
        print('Unexpected comand line arguments. Use format:')
        print('\t' + help_msg)
        sys.exit()

    graph = read_graph(filename)[0]
    print(can_share(graph, a, x=src, y=dst))


if __name__ == "__main__":
    main(sys.argv[1:])
