import json
from graphify.cache import check_semantic_cache
from pathlib import Path

detect = json.loads(Path(".graphify_detect.json").read_text())
all_files = [f for files in detect["files"].values() for f in files]

cached_nodes, cached_edges, cached_hyperedges, uncached = check_semantic_cache(all_files)

if cached_nodes or cached_edges or cached_hyperedges:
    Path(".graphify_cached.json").write_text(json.dumps({"nodes": cached_nodes, "edges": cached_edges, "hyperedges": cached_hyperedges}))
Path(".graphify_uncached.txt").write_text("\n".join(uncached))
total = len(all_files)
uncached_n = len(uncached)
cached_n = total - uncached_n
print(f"Cache: {cached_n} files hit, {uncached_n} files need extraction")
print("Uncached files:")
for f in uncached:
    print(" ", f)
