# Databricks notebook source

from pathlib import Path

volume_path = Path("/Volumes/workspace/market_data/raw_market_data")

print(f"Volume exists: {volume_path.exists()}")
print(f"Volume writable: {volume_path.is_dir()}")

test_dir = volume_path / "_smoke_test"
test_dir.mkdir(exist_ok=True)

test_file = test_dir / "access_test.txt"
test_file.write_text("Unity Catalog Volume access verified")

print(f"Written: {test_file}")
print(f"Read back: {test_file.read_text()}")
