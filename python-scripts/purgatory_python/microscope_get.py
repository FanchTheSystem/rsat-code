#!/usr/bin/python
#-*-coding: utf-8-*-

##### ---------- imports ---------- #####

#Used to set parser and subparsers
from microscope_parser import *
from workflows_functions import *
from microscope_functions import *

import sys


##### ---------- Main Program ---------- #####
if __name__ == '__main__':

    args = microscope_parser()

    if args.sp is None:
        help_message()
    elif args.sp == 'organisms':
        retrieve_microscope_species(args.output, args.verbosity)
    elif args.sp == 'gpr':
        genomicObjects_by_orgname(args.org, args.output, args.verbosity)
    elif args.sp == 'reactionInfo':
        get_MetaCycReaction(args.mrId, args.output, args.verbosity)
    elif args.sp == 'reactionList':
        get_MetaCycReactionFromOrg(args.org, args.output, args.verbosity)
    elif args.sp == 'reactions':
        allReactionList(args.output, args.verbosity)
        
        
