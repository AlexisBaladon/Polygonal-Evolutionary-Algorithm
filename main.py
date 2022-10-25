import argparse
import sys
import prueba

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
    return

if __name__ == "__main__":
    main()