import re
import subprocess
import os

def compile_thesis():
    print("Step 1: Compiling LaTeX to Typst using Pandoc...")
    # Run pandoc
    cmd_pandoc = [
        r'C:\Users\Rezvi\AppData\Local\Pandoc\pandoc.exe',
        '-s',
        'report.tex',
        '-o',
        'report.typ'
    ]
    subprocess.run(cmd_pandoc, check=True)
    print("Typst file report.typ created.")

    print("Step 2: Post-processing Typst file for column widths...")
    with open('report.typ', 'r', encoding='utf-8') as f:
        content = f.read()

    # Define our custom column specifications for each of the 15 tables
    # in order of appearance (0 to 14)
    custom_cols = [
        # Match 0: Course (Cover page)
        '(1.5fr, 3.5fr)',
        # Match 1: Submitted by (Cover page)
        '(1.2fr, 1.8fr)',
        # Match 2: Submitted to (Cover page)
        '(1fr)',
        # Match 3: Table 1 (Datasets)
        '(1.3fr, 2.3fr, 0.8fr, 0.8fr, 1.8fr)',
        # Match 4: Table 2 (Commodity mapping)
        '(1.2fr, 4fr)',
        # Match 5: Table 3 (Debt indicators)
        '(1.8fr, 2.2fr, 2.5fr)',
        # Match 6: Table 4 (Null counts)
        '(2.8fr, 1fr, 1fr)',
        # Match 7: Table 5 (Descriptive statistics)
        '(3.2fr, 0.9fr, 1.2fr, 1.2fr, 0.9fr, 0.9fr, 0.9fr, 0.9fr, 0.9fr)',
        # Match 8: Table 6 (Model comparison prices)
        '(1.8fr, 2fr, 1fr, 1fr, 1fr)',
        # Match 9: Table 7 (Model comparison debt)
        '(2.5fr, 2fr, 1fr, 1fr, 1fr)',
        # Match 10: Table 8 (K-Means centers)
        '(1fr, 1.8fr, 1.5fr, 1.5fr, 1.5fr, 1.8fr, 1.2fr)',
        # Match 11: Table 9 (Division-year counts)
        '(1.5fr, 1fr, 1fr, 1.2fr)',
        # Match 12: Table 10 (Interactive demo)
        '(1.5fr, 2.5fr, 3.5fr)',
        # Match 13: Table 11 (Appendix A divisions)
        '(1fr, 1fr)',
        # Match 14: Table 12 (Appendix C column dictionary)
        '(2.5fr, 1fr, 3fr)'
    ]

    # Find all #table( blocks in report.typ
    table_starts = [m.start() for m in re.finditer(r'#table\(', content)]
    
    if len(table_starts) != len(custom_cols):
        print(f"WARNING: Found {len(table_starts)} tables in typst, but expected {len(custom_cols)}!")
        num_to_process = min(len(table_starts), len(custom_cols))
    else:
        num_to_process = len(table_starts)

    new_content = ""
    last_idx = 0
    
    for i in range(num_to_process):
        start = table_starts[i]
        # Append content from last processed end to this table start
        new_content += content[last_idx:start]
        
        # Define search boundary to prevent crossing into next table
        end_search = table_starts[i+1] if i + 1 < len(table_starts) else len(content)
        sub_segment = content[start:end_search]
        
        # Replace the first occurrence of columns: ... in this subsegment
        m_col = re.search(r'columns:\s*(\d+|\([^\)]+\)),', sub_segment)
        if m_col:
            orig_col_spec = m_col.group(0)
            new_col_spec = f"columns: {custom_cols[i]},"
            replaced_segment = sub_segment.replace(orig_col_spec, new_col_spec, 1)
            new_content += replaced_segment
        else:
            print(f"Could not find columns definition in table {i}!")
            new_content += sub_segment
            
        last_idx = end_search
        
    # Append any remaining content after the last processed table segment
    new_content += content[last_idx:]

    with open('report.typ', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Typst file post-processed successfully with custom column widths.")

    print("Step 3: Compiling Typst to PDF using Typst CLI...")
    # Compile using typst directly
    cmd_typst = [
        'typst',
        'compile',
        'report.typ',
        'Big Data Analytics - Project Report.pdf'
    ]
    subprocess.run(cmd_typst, check=True)
    print("Compilation completed successfully: Big Data Analytics - Project Report.pdf created.")

if __name__ == '__main__':
    compile_thesis()
