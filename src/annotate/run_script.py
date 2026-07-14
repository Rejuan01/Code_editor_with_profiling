import sys
import subprocess
import os

def run_profiling_pipeline(cpp_filename):
    """
    Compiles a C++ file and runs it through Valgrind Cachegrind.
    Outputs the raw machine-readable data to 'annotation.txt'.
    """
    if not os.path.exists(cpp_filename):
        print(f"[Error] The file '{cpp_filename}' does not exist.")
        sys.exit(1)

    # Create a temporary name for the executable (e.g., main.cpp -> main_exec)
    base_name = os.path.splitext(os.path.basename(cpp_filename))[0]
    exec_name = f"./{base_name}_exec"
    output_file = "annotation.txt"

    print(f"\n[1/3] Compiling '{cpp_filename}' with debug symbols (-g)...")
    compile_cmd = ["g++", "-g", "-O0", cpp_filename, "-o", exec_name]
    
    try:
        # check=True ensures the script stops if there is a syntax error in the C++ code
        subprocess.run(compile_cmd, check=True)
        print("      -> Compilation successful.")
    except subprocess.CalledProcessError:
        print("[Error] Compilation failed. Please check your C++ syntax.")
        sys.exit(1)

    print(f"\n[2/3] Running Cachegrind (Simulating Cache & Branch Prediction)...")
    print("      -> This may take a moment depending on the C++ program's complexity.")
    
    profiler_cmd = [
        "valgrind", 
        "--tool=cachegrind", 
        "--branch-sim=yes", 
        "--cache-sim=yes", 
        f"--cachegrind-out-file={output_file}", 
        exec_name
    ]
    
    try:
        # We run the command. Valgrind will output some text to the terminal, 
        # but the actual data is piped directly into annotation.txt
        subprocess.run(profiler_cmd, check=True)
        print(f"      -> Profiling complete. Data saved to '{output_file}'.")
    except subprocess.CalledProcessError:
        print("[Error] Valgrind execution failed.")
        sys.exit(1)

    print("\n[3/3] Cleaning up temporary executable...")
    if os.path.exists(exec_name):
        os.remove(exec_name)
        print("      -> Clean up finished.")
        
    print(f"\n[SUCCESS] Profiling done! You can now run your parser on '{output_file}'.\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 ./annotate/run_script.py <filename.cpp>")
        print("Example: python3 ./annotate/run_script.py main.cpp")
        sys.exit(1)
        
    target_cpp_file = sys.argv[1]
    run_profiling_pipeline(target_cpp_file)