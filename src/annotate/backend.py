import json
import os

def parse_machine_readable_valgrind(filepath, target_file_name="main.cpp"):
    """
    Parses a machine-readable Valgrind output file (Callgrind/Cachegrind format).
    Dynamically maps events and calculates line-level execution percentages.
    """
    events = []
    summary_totals = []
    line_data = {}
    current_file = ""
    
    print(f"--- Starting Parser for {filepath} ---")
    print(f"--- Filtering for target C++ file: {target_file_name} ---\n")

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # 1. Catch Events (e.g., "events: Ir I1mr DLmr")
                if line.startswith("events:"):
                    events = line.split()[1:]
                    print(f"[*] Detected Events: {events}")
                    continue
                    
                # 2. Catch Summary (e.g., "summary: 1747376244")
                # We need this total to calculate accurate percentages
                if line.startswith("summary:"):
                    summary_totals = [int(x.replace(',', '')) for x in line.split()[1:]]
                    print(f"[*] Detected Program Totals: {summary_totals}")
                    continue
                    
                # 3. Track the current file being analyzed
                if line.startswith("fl="):
                    # Extract the filename from the path (e.g., "./main.cpp" -> "main.cpp")
                    current_file = line.split("=")[1]
                    continue
                    
                # 4. Parse line data (Lines starting with a number)
                if line[0].isdigit():
                    # Crucial: Only parse lines that belong to the user's specific C++ file
                    if target_file_name not in current_file:
                        continue
                        
                    parts = line.split()
                    line_num = int(parts[0])
                    metrics = [int(x) for x in parts[1:]]
                    
                    # Initialize the dictionary for this line if we haven't seen it yet
                    if line_num not in line_data:
                        line_data[line_num] = {event: 0 for event in events}
                        
                    # Map the numbers to their respective event names
                    for i, event in enumerate(events):
                        if i < len(metrics):
                            line_data[line_num][event] += metrics[i]

    except FileNotFoundError:
        return f"Error: The file '{filepath}' was not found. Please check the name."

    # 5. Format the results into clean JSON
    results = []
    
    # Safely get the total Instructions (Ir) to calculate percentages
    # We default to 1 to prevent division by zero if summary is missing
    total_ir = summary_totals[0] if summary_totals and len(summary_totals) > 0 else 1
    
    # Dictionary to translate Valgrind abbreviations into human-readable JSON keys
    friendly_names = {
        "D1mr": "l1_cache_misses",
        "DLmr": "llc_cache_misses",
        "Bc": "branches_executed",
        "Bcm": "branch_misses",
        "Bim": "indirect_branch_misses"
    }
    
    for line_num, metrics in sorted(line_data.items()):
        ir_count = metrics.get("Ir", 0)
        percentage = (ir_count / total_ir) * 100 if total_ir > 0 else 0
        
        # We only want to include lines that actually consumed CPU time (> 0.0%)
        if percentage > 0.0:
            result_item = {
                "line": line_num,
                "percentage": round(percentage, 4), # Keep 4 decimals for precision
                "raw_instructions": ir_count
            }
            
            # Dynamically add cache and branch metrics with friendly names
            for event, val in metrics.items():
                if event != "Ir" and val > 0:
                    key_name = friendly_names.get(event, event) # Use friendly name if it exists
                    result_item[key_name] = val
                    
            results.append(result_item)
            
    # Sort results so the most expensive lines (highest percentage) appear at the top
    results.sort(key=lambda x: x["percentage"], reverse=True)
    
    return json.dumps(results, indent=2)

if __name__ == "__main__":
    import sys
    
    # =====================================================================
    # Use command-line arguments if provided, else defaults
    # =====================================================================
    if len(sys.argv) >= 3:
        YOUR_FILE_NAME = sys.argv[1]
        TARGET_SOURCE_FILE = sys.argv[2]
    else:
        YOUR_FILE_NAME = "annotation.txt" 
        TARGET_SOURCE_FILE = "main.cpp"
    
    # =====================================================================
    
    # If the file doesn't exist (because you are testing on this webpage),
    # this creates a mock file matching the exact format you provided earlier!
    if not os.path.exists(YOUR_FILE_NAME):
        print(f"Creating mock '{YOUR_FILE_NAME}' for demonstration...\n")
        with open(YOUR_FILE_NAME, "w") as f:
            # We add D1mr (L1 Cache), DLmr (LLC Cache), Bc (Branches), and Bcm (Branch Misses)
            f.write("events: Ir D1mr DLmr Bc Bcm\n")
            f.write("summary: 1747376244 5000000 100000 80000000 3000000\n")
            f.write("fl=./csu/libc-start.c\n")
            f.write("128 200000 100 5 300 10\n")  # System code (should be ignored)
            f.write("fl=/home/sheikh/Documents/bottleneck_analysis/main.cpp\n")
            f.write("fn=main\n")
            f.write("21 130000013 150000 8000 400000 15000\n") # 7.44%, high instructions
            f.write("26 100000021 500 10 9000000 2500000\n")  # 5.72%, massive branch misses!
            f.write("15 30000001 2500000 95000 1000 5\n")       # 1.72%, massive cache misses!
            
    # Run the parser
    final_json_output = parse_machine_readable_valgrind(YOUR_FILE_NAME, TARGET_SOURCE_FILE)
    
    print("\n=== FINAL PARSED JSON OUTPUT ===")
    print(final_json_output)