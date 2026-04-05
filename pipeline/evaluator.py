import json
import pandas as pd
from pathlib import Path
from typing import Dict, List
from rich.table import Table
from rich.console import Console

console = Console()

CATEGORIES = [
    "reentrancy", "integer_overflow", "access_control", 
    "timestamp_dependence", "unchecked_calls", "tx_origin", 
    "uninitialized_storage", "short_address"
]

class Evaluator:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.report_file = self.results_dir / "evaluation_report.json"
        self.results_dir.mkdir(exist_ok=True)
    
    def load_results(self, tool_name: str) -> List[Dict]:
        file_path = self.results_dir / f"{tool_name}_results.json"
        if not file_path.exists():
            console.print(f"[red]No {tool_name} results found[/red]")
            return []
        return json.load(open(file_path))
    
    def get_detected_categories(self, tool_results: List[Dict], contract_name: str) -> set:
        categories = set()
        for result in tool_results:
            if result["contract"] == contract_name:
                categories.update([issue["category"] for issue in result["issues"]])
        return categories
    
    def compute_metrics(self, hyscav_results: List[Dict], ground_truth_results: List[Dict]):
        metrics = {cat: {"TP": 0, "FP": 0, "FN": 0} for cat in CATEGORIES}
        overall = {"TP": 0, "FP": 0, "FN": 0}
        
        for h_result in hyscav_results:
            contract = h_result["contract"]
            h_cats = set(h_result["issues"])
            
            gt_cats = self.get_detected_categories(ground_truth_results, contract)
            
            for cat in CATEGORIES:
                if cat in h_cats and cat in gt_cats:
                    metrics[cat]["TP"] += 1
                    overall["TP"] += 1
                elif cat in h_cats:
                    metrics[cat]["FP"] += 1
                    overall["FP"] += 1
                elif cat in gt_cats:
                    metrics[cat]["FN"] += 1
                    overall["FN"] += 1
        
        df = pd.DataFrame({
            "Category": CATEGORIES + ["Overall"],
            "Precision": [self.precision(metrics[cat]) for cat in CATEGORIES] + [self.precision(overall)],
            "Recall": [self.recall(metrics[cat]) for cat in CATEGORIES] + [self.recall(overall)],
            "F1": [self.f1(metrics[cat]) for cat in CATEGORIES] + [self.f1(overall)]
        })
        
        return df, metrics
    
    @staticmethod
    def precision(stats: Dict) -> float:
        tp = stats["TP"]
        fp = stats["FP"]
        return tp / (tp + fp) if (tp + fp) > 0 else 0.0
    
    @staticmethod
    def recall(stats: Dict) -> float:
        tp = stats["TP"]
        fn = stats["FN"]
        return tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    @staticmethod
    def f1(stats: Dict) -> float:
        p = Evaluator.precision(stats)
        r = Evaluator.recall(stats)
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    
    def run(self):
        hyscav_res = self.load_results("hyscav")
        slither_res = self.load_results("slither")
        myth_res = self.load_results("mythril")
        
        ground_truth = slither_res + myth_res  # Union as GT
        
        df, metrics = self.compute_metrics(hyscav_res, ground_truth)
        
        table = Table(title="hy-scav Evaluation vs Slither+Mythril")
        table.add_column("Category", style="cyan")
        table.add_column("Precision", justify="right")
        table.add_column("Recall", justify="right")
        table.add_column("F1", justify="right")
        
        for _, row in df.iterrows():
            table.add_row(
                str(row["Category"]),
                f"{row['Precision']:.3f}",
                f"{row['Recall']:.3f}",
                f"{row['F1']:.3f}"
            )
        
        console.print(table)
        
        report = {"metrics": df.to_dict('records'), "raw_stats": metrics}
        self.report_file.write_text(json.dumps(report, indent=2))
        console.print(f"[green]Full report: {self.report_file}[/green]")

