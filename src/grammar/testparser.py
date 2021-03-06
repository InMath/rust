#!/usr/bin/env python
#
# Copyright 2015 The Rust Project Developers. See the COPYRIGHT
# file at the top-level directory of this distribution and at
# http://rust-lang.org/COPYRIGHT.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.
import sys

import os
import subprocess
import argparse

# usage: testparser.py [-h] [-p PARSER [PARSER ...]] -s SOURCE_DIR

# Parsers should read from stdin and return exit status 0 for a
# successful parse, and nonzero for an unsuccessful parse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--parser', nargs='+')
parser.add_argument('-s', '--source-dir', nargs=1, required=True)
args = parser.parse_args(sys.argv[1:])

total = 0
ok = {}
bad = {}
for parser in args.parser:
    ok[parser] = 0
    bad[parser] = []
devnull = open(os.devnull, 'w')
print "\n"

for base, dirs, files in os.walk(args.source_dir[0]):
    for f in filter(lambda p: p.endswith('.rs'), files):
        p = os.path.join(base, f)
        compile_fail = 'compile-fail' in p
        ignore = any('ignore-test' in line or 'ignore-lexer-test' in line
                     for line in open(p).readlines())
        if compile_fail or ignore:
            continue
        total += 1
        for parser in args.parser:
            if subprocess.call(parser, stdin=open(p), stderr=subprocess.STDOUT, stdout=devnull) == 0:
                ok[parser] += 1
            else:
                bad[parser].append(p)
        parser_stats = ', '.join(['{}: {}'.format(parser, ok[parser]) for parser in args.parser])
        sys.stdout.write("\033[K\r total: {}, {}, scanned {}"
                         .format(total, os.path.relpath(parser_stats), os.path.relpath(p)))

devnull.close()

print "\n"

for parser in args.parser:
    filename = os.path.basename(parser) + '.bad'
    print("writing {} files that failed to parse with {} to {}".format(len(bad[parser]), parser, filename))
    with open(filename, "w") as f:
          for p in bad[parser]:
              f.write(p)
              f.write("\n")
