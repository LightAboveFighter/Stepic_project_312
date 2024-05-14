from do_tables import do_a_site_with_tables
import argparse
 
parser = argparse.ArgumentParser(description="Creating tables")
parser.add_argument("class_id", type=int, help="The class id")
parser.add_argument("update", type=str, help="Indicates the need to update (or write for the first time) data about the class")
parser.add_argument("-s", "--session_info",  action="store_true", help="If you don't have file 'Session_information.txt'")
args = parser.parse_args()

if str.lower(args.update) == "true":
    update = True
elif str.lower(args.update) == "false":
    update = False
else:
    print("Incorrect update information")

if args.session_info:
    client_id = str(input("Enter your client_id: "))
    client_secret = str(input("Enter your client_secret: "))
    do_a_site_with_tables(args.class_id, update, client_id, client_secret)
else:
    do_a_site_with_tables(args.class_id, update)
print("done")
