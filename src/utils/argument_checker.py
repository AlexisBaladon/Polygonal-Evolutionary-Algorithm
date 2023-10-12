import os

class ArgumentChecker:
    def __init__(self):
        return
    
    def check_preconditions(self, args):
        # Check values' domain
        if args["width"] is not None and args["width"] <= 0:
            raise Exception("Width must be greater than 0")
        if args["height"] is not None and args["height"] <= 0:
            raise Exception("Height must be greater than 0")
        if args["vertex_count"] is not None and args["vertex_count"] < 5:
            raise Exception("Vertex count must be greater than 4")
        if args["cpu_count"] < 1:
            raise Exception("CPU count must be greater than 0")
        if args["edge_rate"] < 0 or args["edge_rate"] > 1:
            raise Exception("Edge rate must be between 0 and 1")
        if args["manual_console"] != 0 and args["manual_console"] != 1:
            raise Exception("manual_console is a boolean value")
        if args["verbose"] != 0 and args["verbose"] != 1:
            raise Exception("verbose is a boolean value")
        if args["show"] != 0 and args["show"] != 1:
            raise Exception("show is a boolean value")
        if args["selection"] not in ["best", "tournament"]:
            raise Exception("Selection method must be one of the following: best, tournament")
        if args["selection"] == "tournament" and args["tournament_size"] < 1:
            raise Exception("Tournament size must be greater than 0")
        
        # Check directories
        if not os.path.isdir(args["input_path"]):
            raise Exception(f"Input path {args['input_path']} does not exist")
        if not os.path.isdir(args["output_path"]):
            raise Exception("Output path does not exist")
        return args

    def process_arguments(self, get_arguments):
        try:
            args = get_arguments()
            args = self.check_preconditions(args)
        except Exception as e:
            print(str(e))
        return args