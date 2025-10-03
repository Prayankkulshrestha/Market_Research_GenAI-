from workflow import run_graph
import config

config.set_date_range("2025-09-01", "2025-03-01")
print(config.START_DATE)
print(config.END_DATE)


state = {"category":"Energy Drinks"}
results = run_graph(state=state)
print("From cache?", results.get("_from_cache"))
print("Final report:", results.get("final_report"))