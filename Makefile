.PHONY: info-tree

# frplib/data/info_tree.py is generated from info-manifest.txt and is
# gitignored; regenerate it whenever the manifest changes.
info-tree: src/frplib/data/info_tree.py

src/frplib/data/info_tree.py: src/frplib/data/info-manifest.txt src/frplib/repls/info.py src/frplib/repls/info_types.py
	hatch run python -m frplib.repls.info
