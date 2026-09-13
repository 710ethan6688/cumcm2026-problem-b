from __future__ import annotations

import ast
from pathlib import Path
import unicodedata

from PIL import Image, ImageDraw, ImageFont
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Comment, Keyword, Name, Number, Operator, String, Token


HERE = Path(__file__).resolve().parent
SOURCE_PATH = HERE / "q1_geometry.py"
OUTPUT_DIR = HERE.parent / "output" / "figures"

PAGE_WIDTH = 2480
PAGE_HEIGHT = 3508
LEFT_MARGIN = 122
RIGHT_MARGIN = 100
HEADER_HEIGHT = 245
FOOTER_HEIGHT = 100
LINE_NUMBER_WIDTH = 92
CODE_FONT_SIZE = 25
LINE_HEIGHT = 37

MONO_FONT = Path(r"C:\Windows\Fonts\CascadiaMono.ttf")
CJK_FONT = Path(r"C:\Windows\Fonts\msyh.ttc")
TITLE_FONT = Path(r"C:\Windows\Fonts\simhei.ttf")

PAGES = (
    (
        "q1_key_code_1.png",
        "Q1关键代码（一）：示向约束与半平面交",
        ("bearing_halfplanes", "halfplane_intersection_main"),
    ),
    (
        "q1_key_code_2.png",
        "Q1关键代码（二）：直径计算与圆盘覆盖判定",
        ("diameter_rotating_calipers", "coverage_by_dot_product"),
    ),
)


def _extract_functions(source: str, names: tuple[str, ...]) -> str:
    """按函数名从当前正式源码中抽取完整实现。"""

    tree = ast.parse(source)
    lines = source.splitlines()
    blocks: list[str] = []
    nodes = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for name in names:
        node = nodes.get(name)
        if node is None or node.end_lineno is None:
            raise ValueError(f"未在正式源码中找到函数：{name}")
        blocks.append("\n".join(lines[node.lineno - 1 : node.end_lineno]))
    return "\n\n".join(blocks) + "\n"


def _display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1 for char in text)


def _token_color(token_type: Token) -> str:
    if token_type in Comment:
        return "#667085"
    if token_type in Keyword:
        return "#7F56D9"
    if token_type in Name.Function or token_type in Name.Class:
        return "#175CD3"
    if token_type in Name.Builtin:
        return "#026AA2"
    if token_type in String:
        return "#067647"
    if token_type in Number:
        return "#B54708"
    if token_type in Operator:
        return "#344054"
    return "#101828"


def _tokenized_lines(source: str) -> list[list[tuple[str, str]]]:
    result: list[list[tuple[str, str]]] = [[]]
    for token_type, value in lex(source, PythonLexer()):
        color = _token_color(token_type)
        pieces = value.split("\n")
        for index, piece in enumerate(pieces):
            if piece:
                result[-1].append((piece, color))
            if index < len(pieces) - 1:
                result.append([])
    if result and not result[-1]:
        result.pop()
    return result


def _draw_fixed_width_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    segments: list[tuple[str, str]],
    mono_font: ImageFont.FreeTypeFont,
    cjk_font: ImageFont.FreeTypeFont,
    cell_width: float,
) -> None:
    x, y = position
    column = 0
    for text, color in segments:
        for char in text.expandtabs(4):
            is_cjk = unicodedata.east_asian_width(char) in {"W", "F"}
            font = cjk_font if is_cjk else mono_font
            draw.text((x + column * cell_width, y), char, font=font, fill=color)
            column += 2 if is_cjk else 1


def _render_page(filename: str, title: str, source: str) -> Path:
    mono_font = ImageFont.truetype(str(MONO_FONT), CODE_FONT_SIZE)
    cjk_font = ImageFont.truetype(str(CJK_FONT), CODE_FONT_SIZE)
    title_font = ImageFont.truetype(str(TITLE_FONT), 49)
    subtitle_font = ImageFont.truetype(str(CJK_FONT), 25)
    line_number_font = ImageFont.truetype(str(MONO_FONT), 21)
    footer_font = ImageFont.truetype(str(CJK_FONT), 22)

    image = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "#FFFFFF")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, PAGE_WIDTH, HEADER_HEIGHT), fill="#F2F4F7")
    draw.rectangle((0, 0, 22, PAGE_HEIGHT), fill="#175CD3")
    draw.text((LEFT_MARGIN, 60), title, font=title_font, fill="#101828")
    draw.text(
        (LEFT_MARGIN, 142),
        "源文件：q1/code/q1_geometry.py（由正式源码自动抽取）",
        font=subtitle_font,
        fill="#475467",
    )

    code_lines = _tokenized_lines(source)
    available_height = PAGE_HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT - 55
    if len(code_lines) * LINE_HEIGHT > available_height:
        raise ValueError(f"代码共 {len(code_lines)} 行，超过单页可用高度")

    cell_width = mono_font.getlength("0")
    max_columns = max(
        (_display_width("".join(part for part, _ in line).expandtabs(4)) for line in code_lines),
        default=0,
    )
    code_width = max_columns * cell_width
    available_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN - LINE_NUMBER_WIDTH
    if code_width > available_width:
        raise ValueError(f"最长代码行约 {max_columns} 列，超过单页可用宽度")

    separator_x = LEFT_MARGIN + LINE_NUMBER_WIDTH - 24
    draw.line(
        (separator_x, HEADER_HEIGHT + 34, separator_x, PAGE_HEIGHT - FOOTER_HEIGHT - 22),
        fill="#D0D5DD",
        width=2,
    )
    y = HEADER_HEIGHT + 43
    for line_number, segments in enumerate(code_lines, start=1):
        draw.text(
            (LEFT_MARGIN, y + 2),
            f"{line_number:>3}",
            font=line_number_font,
            fill="#98A2B3",
        )
        _draw_fixed_width_text(
            draw,
            (LEFT_MARGIN + LINE_NUMBER_WIDTH, y),
            segments,
            mono_font,
            cjk_font,
            cell_width,
        )
        y += LINE_HEIGHT

    draw.line(
        (LEFT_MARGIN, PAGE_HEIGHT - FOOTER_HEIGHT, PAGE_WIDTH - RIGHT_MARGIN, PAGE_HEIGHT - FOOTER_HEIGHT),
        fill="#E4E7EC",
        width=2,
    )
    draw.text(
        (LEFT_MARGIN, PAGE_HEIGHT - FOOTER_HEIGHT + 30),
        "说明：论文仅展示算法核心；完整可运行源程序见支撑材料。",
        font=footer_font,
        fill="#667085",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    image.save(output_path, format="PNG", dpi=(300, 300), optimize=True)
    return output_path


def main() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    for filename, title, function_names in PAGES:
        excerpt = _extract_functions(source, function_names)
        output_path = _render_page(filename, title, excerpt)
        print(output_path)


if __name__ == "__main__":
    main()
