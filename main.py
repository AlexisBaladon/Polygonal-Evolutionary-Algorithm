import argparse
import sys
import prueba

from AE import AE
from DeapConfig import DeapConfig
from ImageProcessor import ImageProcessor

def get_arguments() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertex_count", type=int, default="./", required=True, help=f"")
    parser.add_argument("--seed", type=str, default="N", required=True, help=f"")
    parser.add_argument("--img_out_dir", type=str, default="./", required=False, help=f"")
    parser.add_argument("--img_in_dir", type=str, default="./", required=False, help=f"")

    args = vars(parser.parse_args())
    return args

def check_preconditions(args):
    return args

def main():
    args = get_arguments()
    args = check_preconditions(args)

    dc = DeapConfig(seed=args["seed"], vertex_count=args["vertex_count"])
    ip = ImageProcessor(img_in_dir=args["img_in_dir"], img_out_dir=args["img_out_dir"])
    ae = AE(dc, ip)

    return

if __name__ == "__main__":
    main()