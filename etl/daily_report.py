import schedule
import pandas as pd
import time
from datetime import datetime
from pathlib import Path

from pipeline import run_pipeline

project_root = Path(__file__).resolve().parent.parent
input_file = project_root / "data" / "processed" / "cleansuperstoredata.csv"
output_file = project_root / "reports" / "sales_product_report.csv"


def run_job():
	run_pipeline()
	df = pd.read_csv(input_file)
	report = df[["Product_Name", "Sales"]]
	report = report.groupby("Product_Name", as_index=False)["Sales"].sum()
	report["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	output_file.parent.mkdir(parents=True, exist_ok=True)
	report.to_csv(output_file, index=False)
	print(f"Report created: {output_file}")


schedule.every().day.at("18:27").do(run_job)
print("Scheduler started. Daily run at 18:27")

while True:
	schedule.run_pending()
	time.sleep(1)