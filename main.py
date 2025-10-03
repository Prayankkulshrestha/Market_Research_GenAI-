from workflow import run_graph
import config
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("--category",help="Category for want insights")
parser.add_argument("--start_date",help="from date you want insight")
parser.add_argument("--end_date",help="Till which date you want insights")

args = parser.parse_args()

start_date = args[1]
end_date= args[2]
category = args[0]

config.set_date_range(end_date=end_date, start_date=start_date)

state = {"category":category}
results = run_graph(state=state)
print("From cache?", results.get("_from_cache"))
print("Final report:", results.get("final_report"))
