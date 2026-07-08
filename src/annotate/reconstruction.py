import re

filename = "./annotate/annotation.txt"
filename2 = "./annotate/summary.txt"

line_no = 0
ans = {}

started = False

percent_re = re.compile(r'\(\s*([\d.]+)%\)')

with open(filename) as f:
    for raw in f:
        line = raw.rstrip()

        # Start from the source code
        if not started:
            if "#include" in line:
                started = True
            else:
                continue

        # End of annotated source
        if line.startswith("--------------------------------------------------------------------------------"):
            break

        # => line: add percentage to previous source line
        if "=>" in line:
            m = percent_re.search(line)
            if m and line_no > 0:
                ans[line_no] += float(m.group(1))
            continue

        # Every remaining line is a source line
        line_no += 1

        m = percent_re.search(line)
        if m:
            ans[line_no] = float(m.group(1))
        else:
            # Empty (.) lines, comments, preprocessor directives, etc.
            ans[line_no] = 0.0

for ln, pct in ans.items():
    print(f"{ln} -> {pct:.2f}%")


# Cleaning the Instruction, cace, branch data

with open(filename2, "r") as f:
    lines = f.readlines()[6:]   # Skip first 7 lines

with open(filename2, "w") as f:
    for line in lines:
        f.write(re.sub(r"^==\d+==\s*", "", line))