import sys
import os
import importlib.util

print("=" * 60)
print("🔍 DIAGNOSTIC TOOL - CHECKING EXTENSIONS")
print("=" * 60)

extensions_to_check = [
    "virus.virus_command",
    "virus.viruslist",
    "virus.local_command",
    "Chip.chip_command",
    "Chip.chips_list",
    "Navi.Pecas",
    "Navi.pecaslist",
    "batalha.batalha",
    "Links.doc_command",
    "Ajuda.sos_command",
    "virus.encontro_command",
    "Mercado.mercado_command",
    "Mercado.trader",
    "Teste.trader_test",
]

for ext in extensions_to_check:
    print(f"\n🔎 Checking: {ext}")
    
    # Convert module name to file path
    parts = ext.split(".")
    file_path = os.path.join(*parts) + ".py"
    
    if os.path.exists(file_path):
        print(f"   ✅ File exists: {file_path}")
        
        # Try to import it
        try:
            spec = importlib.util.spec_from_file_location(ext, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if it has a setup function
            if hasattr(module, "setup"):
                print(f"   ✅ Has setup() function")
            else:
                print(f"   ❌ NO setup() function!")
                
        except Exception as e:
            print(f"   ❌ ERROR importing: {type(e).__name__}: {e}")
    else:
        print(f"   ❌ File NOT found: {file_path}")

print("\n" + "=" * 60)
print("🔍 DIAGNOSTIC COMPLETE")
print("=" * 60)
