import argparse, sys
from suggestions import suggest, InvalidPublicKey

parser = argparse.ArgumentParser(description="Generate a channel open suggestion")

parser.add_argument('pub_key', help="Public key of your node")
parser.add_argument( '--weight:fee_base_msat', help="How strongly to weight lower base fees (0-1)")
parser.add_argument( '--weight:fee_rate_milli_msat', help="How strongly to weight lower rate fees (0-1)")
parser.add_argument( '--weight:peers', help="How strongly to weight highly connected nodes (0-1)")
parser.add_argument( '--weight:distance', help="How strongly to weight distant nodes (0-1)")
parser.add_argument( '--weight:capacity', help="How strongly to weight high-average-capacity nodes (0-1)")
parser.add_argument( '--max:fee_base_msat', help="Exclude nodes with base msat fees higher than this number")
parser.add_argument( '--max:fee_rate_milli_msat', help="Exclude nodes with rate milli msat fees higher than this number")
parser.add_argument( '--max:peers', help="Exclude nodes with more peers than this number")
parser.add_argument( '--min:peers', help="Exclude nodes with fewer peers than this number")
parser.add_argument( '--min:capacity', help="Exclude nodes with lower average capacity than this number")


try:
    __import__("pprint").pprint(suggest(**vars(parser.parse_args())))
except InvalidPublicKey:
    print("Public key not found")

    sys.exit(1)

