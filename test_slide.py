from core.guitar_logic import generate_tab_path

print("Testing basic generation without slide:")
path1 = generate_tab_path(["C", "D"])
for p in path1:
    print(p)

print("\nTesting generation with slide (/D):")
path2 = generate_tab_path(["C", "/D"])
for p in path2:
    print(p)
