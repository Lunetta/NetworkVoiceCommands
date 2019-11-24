import os
import argparse



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("iphost", type=str, help="host specification ip")
    args = parser.parse_args()


    response = os.system("ping -c 1 " + args.iphost)
    #generate_json(args.clients_file)
    if response == 0:
        print("Host "+ args.iphost + " is UP")
    else:
        print ("Host "+ args.iphost + " is DOWN")

