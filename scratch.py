import re

text = """I refs:        1,747,372,306
I1  misses:            2,151
LLi misses:            2,106
I1  miss rate:          0.00%
LLi miss rate:          0.00%
D refs:          812,354,426  (556,286,834 rd   + 256,067,592 wr)
D1  misses:       19,452,067  ( 10,367,743 rd   +   9,084,324 wr)
LLd misses:        7,186,365  (  2,535,507 rd   +   4,650,858 wr)
D1  miss rate:           2.4% (        1.9%     +         3.5%  )
LLd miss rate:           0.9% (        0.5%     +         1.8%  )
LL refs:          19,454,218  ( 10,369,894 rd   +   9,084,324 wr)
LL misses:         7,188,471  (  2,537,613 rd   +   4,650,858 wr)
LL miss rate:            0.3% (        0.1%     +         1.8%  )
Branches:        235,504,722  (205,499,298 cond +  30,005,424 ind)
Mispredicts:       2,094,304  (  2,093,034 cond +       1,270 ind)
Mispred rate:            0.9% (        1.0%     +         0.0%   )"""

def format_summary_text(text):
    html = "<div style='font-family: \"Fira Code\", \"Courier New\", monospace; font-size: 13px; line-height: 1.5; color: #abb2bf;'>"
    color_key = "#61afef"    
    color_num = "#d19a66"    
    color_pct = "#e06c75"    
    color_paren = "#5c6370"  
    
    for line in text.splitlines():
        if not line.strip():
            html += "<br>"
            continue
            
        if ':' in line:
            key, rest = line.split(':', 1)
            formatted_line = f"<span style='color: {color_key}; font-weight: bold;'>{key}:</span>"
            paren_split = rest.split('(', 1)
            val_part = paren_split[0]
            paren_part = f"({paren_split[1]}" if len(paren_split) > 1 else ""
            
            def colorize_numbers(s):
                chunks = s.split('&nbsp;')
                for i, chunk in enumerate(chunks):
                    if not any(c.isdigit() for c in chunk):
                        continue
                    m = re.match(r'^(\(?)?([\d,.]+)(%?)(\)?\s*\w*)?$', chunk)
                    if m:
                        pre, num, pct, post = m.groups()
                        color = color_pct if pct else color_num
                        chunks[i] = f"{pre or ''}<span style='color: {color};'>{num}{pct}</span>{post or ''}"
                return '&nbsp;'.join(chunks)
            
            val_part = val_part.replace(' ', '&nbsp;')
            val_part = colorize_numbers(val_part)
            
            if paren_part:
                paren_part = paren_part.replace(' ', '&nbsp;')
                paren_part = colorize_numbers(paren_part)
                formatted_line += f"{val_part}<span style='color: {color_paren};'>{paren_part}</span>"
            else:
                formatted_line += val_part
                
            html += f"<div>{formatted_line}</div>\n"
        else:
            html += f"<div>{line.replace(' ', '&nbsp;')}</div>\n"
            
    html += "</div>"
    return html

print(format_summary_text(text))
