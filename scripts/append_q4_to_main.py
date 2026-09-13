# -*- coding: utf-8 -*-
import io
from scripts.verify_section6_text import section6_tex

with io.open("c:/Users/23066/Desktop/mathmode/main.tex", "r", encoding="utf-8") as f:
    content = f.read()

target = r"\end{document}"
if target in content:
    # replace the last occurrence of \end{document}
    idx = content.rfind(target)
    new_content = content[:idx] + "\n" + section6_tex.strip() + "\n"
    with io.open("c:/Users/23066/Desktop/mathmode/main.tex", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully appended Section 6 and Section 7 to main.tex!")
else:
    print("Error: \\end{document} not found in main.tex")
