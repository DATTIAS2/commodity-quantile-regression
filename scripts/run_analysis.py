"""Run from the repository root after installing the package."""
import argparse
from pathlib import Path
from commodity_qr.analysis import load_snapshot, prepare_snapshot, synthetic_sample, save_outputs

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--mode", choices=["demo", "historical", "corrected"], default="demo")
parser.add_argument("--specification", choices=["full", "report_reduced", "notebook_reduced"], default="full")
parser.add_argument("--data", type=Path, default=Path("data/local/df3.csv"))
parser.add_argument("--output", type=Path)
args = parser.parse_args()
data = synthetic_sample() if args.mode == "demo" else prepare_snapshot(load_snapshot(args.data), mode=args.mode)
output = args.output or Path("results") / f"{args.mode}_{args.specification}"
label = "Synthetic demonstration - not thesis results" if args.mode == "demo" else f"{args.mode.title()} snapshot analysis / {args.specification}"
_, diagnostics, metadata = save_outputs(data, output, specification=args.specification, label=label)
print(metadata)
print(diagnostics.to_string(index=False))
print(f"Saved to {output}")
