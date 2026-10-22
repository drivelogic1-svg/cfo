# -*- coding: utf-8 -*-
"""
Генератор PDF-справки «Запреты на ввоз товаров в Республике Казахстан (2026)».
По состоянию на 22.10.2026.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, NextPageTemplate, KeepTogether, CondPageBreak,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.flowables import HRFlowable, Flowable

# ----------------------------------------------------------------------------- paths / fonts
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.environ.get("PDF_OUT") or os.path.join(
    ROOT, "Запреты_на_ввоз_товаров_РК_2026.pdf")

def _find_font(filename):
    """Ищет файл шрифта в стандартных каталогах (Linux, macOS, Windows, репозиторий)."""
    candidates = []
    if os.environ.get("FONT_DIR"):
        candidates.append(os.environ["FONT_DIR"])
    candidates += [
        os.path.join(ROOT, "fonts"),
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/dejavu",
        "/usr/share/fonts/TTF",
        "/usr/share/fonts/truetype",
        "/usr/local/share/fonts",
        "/Library/Fonts",
        "/System/Library/Fonts",
        "C:\\Windows\\Fonts",
    ]
    for d in candidates:
        path = os.path.join(d, filename)
        if os.path.isfile(path):
            return path
    raise FileNotFoundError(
        f"Не найден шрифт {filename}. Установите пакет fonts-dejavu-core "
        f"или задайте переменную окружения FONT_DIR."
    )


pdfmetrics.registerFont(TTFont("DVS", _find_font("DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVS-B", _find_font("DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVS-M", _find_font("DejaVuSansMono.ttf")))
pdfmetrics.registerFont(TTFont("SER", _find_font("DejaVuSerif.ttf")))
pdfmetrics.registerFont(TTFont("SER-B", _find_font("DejaVuSerif-Bold.ttf")))
registerFontFamily("DVS", normal="DVS", bold="DVS-B", italic="DVS", boldItalic="DVS-B")
registerFontFamily("SER", normal="SER", bold="SER-B", italic="SER", boldItalic="SER-B")

# ----------------------------------------------------------------------------- palette
NAVY = HexColor("#15314E")
NAVY2 = HexColor("#24486D")
GOLD = HexColor("#B08A3E")
GOLD_L = HexColor("#D8C08A")
INK = HexColor("#1E252C")
GREY = HexColor("#5C6873")
LINE = HexColor("#D4DCE4")
LIGHT = HexColor("#F3F6FA")
LIGHT2 = HexColor("#EAF0F6")
GREEN = HexColor("#1E7A4C")
RED = HexColor("#A5342A")
AMBER = HexColor("#936B12")
WHITE = colors.white

PAGE_W, PAGE_H = A4
LM, RM, TM, BM = 22 * mm, 22 * mm, 24 * mm, 20 * mm
CONTENT_W = PAGE_W - LM - RM  # 166 mm

# ----------------------------------------------------------------------------- styles
S = {}
S["Body"] = ParagraphStyle(
    "Body", fontName="SER", fontSize=9.2, leading=13.4, textColor=INK,
    alignment=TA_JUSTIFY, spaceAfter=5.5,
)
S["Lead"] = ParagraphStyle(
    "Lead", parent=S["Body"], fontSize=10.2, leading=15,
    textColor=NAVY, spaceAfter=7,
)
S["H1"] = ParagraphStyle(
    "H1", fontName="DVS-B", fontSize=14.2, leading=18, textColor=NAVY,
    spaceBefore=2, spaceAfter=1.5,
)
S["H2"] = ParagraphStyle(
    "H2", fontName="DVS-B", fontSize=10.4, leading=13.5, textColor=NAVY2,
    spaceBefore=9, spaceAfter=3.5,
)
S["H3"] = ParagraphStyle(
    "H3", fontName="DVS-B", fontSize=8.9, leading=11.5, textColor=NAVY,
    spaceBefore=6, spaceAfter=2,
)
S["Small"] = ParagraphStyle(
    "Small", fontName="DVS", fontSize=7.5, leading=10.3, textColor=GREY,
    alignment=TA_LEFT,
)
S["SmallJ"] = ParagraphStyle(
    "SmallJ", parent=S["Small"], alignment=TA_JUSTIFY,
)
S["Bullet"] = ParagraphStyle(
    "Bullet", parent=S["Body"], leftIndent=11, bulletIndent=1.5,
    spaceAfter=3.2,
)
S["Num"] = ParagraphStyle(
    "Num", parent=S["Body"], leftIndent=13, bulletIndent=0,
    spaceAfter=3.6,
)
S["Tbl"] = ParagraphStyle(
    "Tbl", fontName="DVS", fontSize=7.45, leading=9.8, textColor=INK,
)
S["TblC"] = ParagraphStyle("TblC", parent=S["Tbl"], alignment=TA_CENTER)
S["TblB"] = ParagraphStyle("TblB", parent=S["Tbl"], fontName="DVS-B")
S["TblH"] = ParagraphStyle(
    "TblH", fontName="DVS-B", fontSize=7.35, leading=9.6, textColor=WHITE,
)
S["TblHC"] = ParagraphStyle("TblHC", parent=S["TblH"], alignment=TA_CENTER)
S["TblSmall"] = ParagraphStyle("TblSmall", parent=S["Tbl"], fontSize=6.9, leading=9.0)
S["TblSmallC"] = ParagraphStyle("TblSmallC", parent=S["TblSmall"], alignment=TA_CENTER)
S["CardLabel"] = ParagraphStyle(
    "CardLabel", fontName="DVS-B", fontSize=7.6, leading=10.2, textColor=NAVY2,
)
S["CardValue"] = ParagraphStyle(
    "CardValue", fontName="SER", fontSize=8.15, leading=11.4, textColor=INK,
)
S["CalloutTitle"] = ParagraphStyle(
    "CalloutTitle", fontName="DVS-B", fontSize=7.7, leading=10, textColor=NAVY,
    spaceAfter=2.5,
)
S["CalloutBody"] = ParagraphStyle(
    "CalloutBody", fontName="SER", fontSize=8.5, leading=12.2, textColor=INK,
    alignment=TA_LEFT,
)
S["TOC0"] = ParagraphStyle(
    "TOC0", fontName="DVS-B", fontSize=9.2, leading=14, textColor=NAVY,
    spaceBefore=3,
)
S["TOC1"] = ParagraphStyle(
    "TOC1", fontName="DVS", fontSize=8.4, leading=12, textColor=GREY,
    leftIndent=12,
)
S["Src"] = ParagraphStyle(
    "Src", fontName="DVS", fontSize=7.3, leading=9.8, textColor=INK,
    leftIndent=12, firstLineIndent=-12, spaceAfter=2.4,
)
S["SrcUrl"] = ParagraphStyle(
    "SrcUrl", fontName="DVS", fontSize=6.7, leading=8.8, textColor=HexColor("#3D5A78"),
    leftIndent=12,
)
S["KpiNum"] = ParagraphStyle(
    "KpiNum", fontName="DVS-B", fontSize=23, leading=25, textColor=NAVY,
)
S["KpiLabel"] = ParagraphStyle(
    "KpiLabel", fontName="DVS", fontSize=6.8, leading=9.2, textColor=GREY,
)


def P(text, style="Body"):
    return Paragraph(text, S[style])


def status(text, color, extra=""):
    tail = f'  <font color="#5C6873">· {extra}</font>' if extra else ""
    return Paragraph(
        f'<font color="{color.hexval()}">●</font> <font color="{color.hexval()}"><b>{text}</b></font>{tail}',
        ParagraphStyle("st", fontName="DVS", fontSize=8.0, leading=10.5, spaceAfter=3.5),
    )


def h1(text, number=None):
    label = f"{number}. {text}" if number else text
    return [Paragraph(label, S["H1"]),
            HRFlowable(width="100%", thickness=1.1, color=GOLD, spaceBefore=1, spaceAfter=8)]


def h2(text):
    return Paragraph(text, S["H2"])


def bullet(text):
    return Paragraph(text, S["Bullet"], bulletText="•")


def numbered(n, text):
    return Paragraph(text, S["Num"], bulletText=f"{n}.")


def callout(title, body, accent=GOLD, bg=LIGHT):
    inner = Table(
        [[P(title, "CalloutTitle")], [P(body, "CalloutBody")]],
        colWidths=[CONTENT_W - 10 * mm],
    )
    inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    t = Table([[inner]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3.0, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6.5),
    ]))
    return t


def data_table(header, rows, widths, align_center_cols=(), header_bg=NAVY, small=False):
    tstyle = S["TblSmall"] if small else S["Tbl"]
    cstyle = S["TblSmallC"] if small else S["TblC"]
    data = [[Paragraph(c, S["TblHC"] if i in align_center_cols else S["TblH"]) for i, c in enumerate(header)]]
    for r in rows:
        data.append([
            c if isinstance(c, Paragraph) else Paragraph(str(c), cstyle if i in align_center_cols else tstyle)
            for i, c in enumerate(r)
        ])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
        ("TOPPADDING", (0, 0), (-1, -1), 4.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.2),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), HexColor("#F5F8FB")))
    t.setStyle(TableStyle(style))
    return t


def card(rows):
    data = [[Paragraph(k, S["CardLabel"]), Paragraph(v, S["CardValue"])] for k, v in rows]
    t = Table(data, colWidths=[40 * mm, CONTENT_W - 40 * mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT2),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.4),
    ]))
    return t


def kpi_row(items):
    cells = []
    for num, label in items:
        cells.append([Paragraph(num, S["KpiNum"]), Paragraph(label, S["KpiLabel"])])
    t = Table([cells], colWidths=[CONTENT_W / len(items)] * len(items), hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("LINEABOVE", (0, 0), (-1, 0), 2.2, GOLD),
        ("LINEBEFORE", (1, 0), (-1, 0), 0.6, WHITE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t



# ----------------------------------------------------------------------------- timeline flowable
class TimelineDiagram(Flowable):
    """Диаграмма периодов действия запретов в 2026 году."""

    ROWS = [
        ("Чай, отдельные наименования", [("05.01", "31.12", "open", "с 05.01.2026, бессрочно")]),
        ("Яйца кур свежие (0407 21)", [("21.04", "21.10", "closed", "21.04 — 21.10.2026")]),
        ("Томаты свежие (0702)", [("22.06", "30.06", "closed", "22.06 — 30.06.2026")]),
        ("Строительные материалы", [("31.05", "17.10", "closed", "31.05 — 17.10.2026")]),
        ("Пшеница (1001)", [("27.07", "31.12", "active", "с 27.07.2026, 6 месяцев")]),
        ("Яблоки свежие (0808 10)", [("03.09", "31.12", "active", "03.09 — 31.12.2026")]),
    ]
    MONTHS = ["янв", "фев", "мар", "апр", "май", "июн",
              "июл", "авг", "сен", "окт", "ноя", "дек"]

    def __init__(self, width, row_h=13.5, label_w=112, head_h=13):
        Flowable.__init__(self)
        self.width = width
        self.row_h = row_h
        self.label_w = label_w
        self.head_h = head_h
        self.legend_h = 16
        self.height = head_h + row_h * len(self.ROWS) + self.legend_h

    @staticmethod
    def _frac(day, month):
        return (month - 1 + (day - 1) / 30.0) / 12.0

    def _x(self, day, month):
        return self.label_w + (self.width - self.label_w) * self._frac(day, month)

    def draw(self):
        c = self.canv
        plot_w = self.width - self.label_w
        col_w = plot_w / 12.0
        top = self.height
        chart_top = top - self.head_h + 2.5
        chart_bottom = self.legend_h

        # alternating month bands
        c.setFillColor(HexColor("#F7F9FC"))
        c.rect(self.label_w, chart_bottom, plot_w, chart_top - chart_bottom, stroke=0, fill=1)
        for i in range(0, 12, 2):
            c.setFillColor(WHITE)
            c.rect(self.label_w + i * col_w, chart_bottom, col_w,
                   chart_top - chart_bottom, stroke=0, fill=1)

        # grid + month labels
        c.setFont("DVS", 5.8)
        for i, m in enumerate(self.MONTHS):
            x = self.label_w + i * col_w
            c.setStrokeColor(HexColor("#E1E8EF"))
            c.setLineWidth(0.35)
            c.line(x, chart_bottom, x, chart_top)
            c.setFillColor(GREY)
            c.drawCentredString(x + col_w / 2, top - 5.6, m)
        c.setStrokeColor(HexColor("#E1E8EF"))
        c.line(self.width, chart_bottom, self.width, chart_top)

        # rows
        for r, (label, bars, *_) in enumerate(self.ROWS):
            y = chart_top - (r + 1) * self.row_h
            c.setFillColor(INK)
            c.setFont("DVS", 6.6)
            c.drawString(0, y + self.row_h / 2 - 2.4, label)
            for s_date, e_date, kind, cap in bars:
                sd, sm = [int(v) for v in s_date.split(".")]
                ed, em = [int(v) for v in e_date.split(".")]
                x0 = self._x(sd, sm)
                x1 = self._x(ed, em) + col_w / 30.0 * (30 - ed + 1)
                x1 = min(x1, self.width)
                color = {"active": GREEN, "closed": HexColor("#A8B4BF"), "open": GOLD}[kind]
                c.setFillColor(color)
                bar_h = self.row_h - 6.0
                c.roundRect(x0, y + 3.0, max(x1 - x0, 2.5), bar_h, 1.6, stroke=0, fill=1)

        # "today" marker
        tx = self._x(22, 10)
        c.saveState()
        c.setStrokeColor(HexColor("#B4453A"))
        c.setLineWidth(0.7)
        c.setDash(2.2, 1.8)
        c.line(tx, chart_bottom, tx, chart_top)
        c.restoreState()

        # axis
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.line(0, chart_bottom, self.width, chart_bottom)

        # legend
        ly = 4.0
        items = [(GREEN, "действует"), (HexColor("#A8B4BF"), "прекратил действие"),
                 (GOLD, "бессрочная санитарная мера")]
        x = 0
        for color, text in items:
            c.setFillColor(color)
            c.roundRect(x, ly, 9, 4.6, 1.4, stroke=0, fill=1)
            c.setFillColor(GREY)
            c.setFont("DVS", 5.8)
            c.drawString(x + 12, ly + 0.6, text)
            x += 12 + c.stringWidth(text, "DVS", 5.8) + 16
        c.setFillColor(GREY)
        c.setFont("DVS", 5.8)
        c.drawRightString(self.width, ly + 0.6, "пунктир — дата подготовки справки 22.10.2026")

    def wrap(self, *args):
        return self.width, self.height


# ----------------------------------------------------------------------------- page decorations
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_total(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_total(self, page_count):
        if self._pageNumber == 1:
            return
        self.setFont("DVS", 7.2)
        self.setFillColor(GREY)
        self.drawRightString(PAGE_W - RM, 12 * mm, f"{self._pageNumber} / {page_count}")


def tracked_text(c, x, y, text, font, size, char_space=1.0, color=None):
    if color is not None:
        c.setFillColor(color)
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(char_space)
    t.textOut(text)
    c.drawText(t)


def cover_page(c, doc):
    c.saveState()
    c.setFillColor(WHITE)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    band_h = 78 * mm
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - band_h, PAGE_W, band_h, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(0, PAGE_H - band_h, 58 * mm, 3.2 * mm, stroke=0, fill=1)

    tracked_text(c, LM, PAGE_H - 27 * mm, "РЕСПУБЛИКА КАЗАХСТАН",
                 "DVS-B", 7.2, 1.9, GOLD)

    c.setFillColor(HexColor("#D7E1EA"))
    c.setFont("DVS", 7.8)
    c.drawString(LM, PAGE_H - 35 * mm, "Регулирование внешней торговли  ·  комплаенс ВЭД")

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.7)
    c.line(LM, PAGE_H - 42 * mm, LM + 33 * mm, PAGE_H - 42 * mm)

    c.setFillColor(WHITE)
    c.setFont("DVS-B", 10.5)
    c.drawString(LM, PAGE_H - 55 * mm, "АНАЛИТИЧЕСКАЯ СПРАВКА")
    c.setFillColor(HexColor("#AFC2D3"))
    c.setFont("DVS", 7.6)
    c.drawString(LM, PAGE_H - 62 * mm, "Проверка действующих нормативных правовых актов")

    # eyebrow
    tracked_text(c, LM, PAGE_H - 94 * mm, "ПРАВОВАЯ СПРАВКА  ·  ОКТЯБРЬ 2026",
                 "DVS-B", 8.4, 1.2, GOLD)

    # title
    c.setFillColor(NAVY)
    c.setFont("DVS-B", 26.5)
    c.drawString(LM, PAGE_H - 111 * mm, "ЗАПРЕТЫ НА ВВОЗ ТОВАРОВ")
    c.drawString(LM, PAGE_H - 126 * mm, "В РЕСПУБЛИКЕ КАЗАХСТАН")

    # subtitle
    c.setFillColor(GREY)
    c.setFont("SER", 11.2)
    c.drawString(LM, PAGE_H - 141 * mm, "Проверка нормативных правовых актов 2026 года")
    c.drawString(LM, PAGE_H - 148 * mm, "и действующих ограничений внешней торговли")

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.4)
    c.line(LM, PAGE_H - 157 * mm, LM + 52 * mm, PAGE_H - 157 * mm)

    # key finding box
    box_top = PAGE_H - 167 * mm
    box_h = 47 * mm
    c.setFillColor(LIGHT)
    c.rect(LM, box_top - box_h, 118 * mm, box_h, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(LM, box_top - box_h, 3 * mm, box_h, stroke=0, fill=1)

    tracked_text(c, LM + 8 * mm, box_top - 9 * mm, "ГЛАВНЫЙ ВЫВОД",
                 "DVS-B", 7.6, 0.8, NAVY)

    text = ("Единого постановления Правительства РК, запрещающего ввоз товаров, "
            "в 2026 году не принималось. Запреты вводились приказами министров. "
            "На 22 октября 2026 года действуют запреты на ввоз пшеницы, яблок "
            "и отдельных наименований чая, а также постоянный запрет на ввоз вейпов.")
    c.setFillColor(INK)
    c.setFont("SER", 8.7)
    lines = simpleSplit(text, "SER", 8.7, 104 * mm)
    y = box_top - 16.5 * mm
    for ln in lines:
        c.drawString(LM + 8 * mm, y, ln)
        y -= 4.4 * mm

    # key figures row
    figs = [("4", "действующих\nзапрета"),
            ("3", "прекратили\nдействие"),
            ("0", "постановлений\nПравительства о запрете")]
    fx = LM
    fw = CONTENT_W / 3
    for num, label in figs:
        c.setFillColor(NAVY)
        c.setFont("DVS-B", 21)
        c.drawString(fx, PAGE_H - 227 * mm, num)
        c.setFillColor(GREY)
        c.setFont("DVS", 6.8)
        yy = PAGE_H - 232 * mm
        for line in label.split("\n"):
            c.drawString(fx + 11 * mm, yy, line)
            yy -= 3.4 * mm
        fx += fw

    # meta block
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(LM, 55 * mm, PAGE_W - RM, 55 * mm)

    meta = [
        ("ДАТА ПОДГОТОВКИ", "22 октября 2026 г."),
        ("ПЕРИОД ПРОВЕРКИ", "1 января — 22 октября 2026 г."),
        ("ОБЪЕКТ", "НПА Республики Казахстан о запретах на ввоз товаров"),
        ("ИСТОЧНИКИ", "ИПС «Әділет», официальные публикации, сообщения госорганов"),
    ]
    y = 48 * mm
    for label, value in meta:
        tracked_text(c, LM, y, label, "DVS-B", 6.4, 0.7, GOLD)
        c.setFillColor(NAVY)
        c.setFont("DVS", 7.9)
        c.drawString(LM + 39 * mm, y, value)
        y -= 7.2 * mm

    c.setFillColor(GREY)
    c.setFont("DVS", 6.4)
    c.drawString(LM, 15 * mm,
                 "Подготовлено на основе открытых источников  ·  не является юридическим заключением")
    c.drawRightString(PAGE_W - RM, 15 * mm, "внутренний материал")
    c.restoreState()


def body_page(c, doc):
    c.saveState()
    # header
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.line(LM, PAGE_H - 16 * mm, PAGE_W - RM, PAGE_H - 16 * mm)

    c.setFillColor(GREY)
    c.setFont("DVS", 7.0)
    c.drawString(LM, PAGE_H - 13.4 * mm,
                 "Правовая справка  ·  Запреты на ввоз товаров в Республике Казахстан")
    c.setFillColor(NAVY)
    c.setFont("DVS-B", 7.0)
    c.drawRightString(PAGE_W - RM, PAGE_H - 13.4 * mm, "22.10.2026")

    # footer
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.line(LM, 17 * mm, PAGE_W - RM, 17 * mm)
    c.setFillColor(GREY)
    c.setFont("DVS", 6.3)
    c.drawString(LM, 12 * mm,
                 "Источники: ИПС «Әділет», официальные публикации, сообщения государственных органов")
    c.restoreState()


# ----------------------------------------------------------------------------- document
doc = BaseDocTemplate(
    OUT, pagesize=A4,
    leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
    title="Запреты на ввоз товаров в Республике Казахстан (2026)",
    author="Аналитическая справка",
    subject="Проверка нормативных правовых актов 2026 года",
    creator="ReportLab",
    keywords="Казахстан, запрет ввоза, 2026, приказ, постановление, ЕАЭС, импорт, ВЭД",
    lang="ru-RU",
)

cover_frame = Frame(LM, BM, CONTENT_W, PAGE_H - TM - BM, id="cover",
                    leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
body_frame = Frame(LM, BM, CONTENT_W, PAGE_H - TM - BM, id="body",
                   leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

doc.addPageTemplates([
    PageTemplate(id="cover", frames=[cover_frame], onPage=cover_page),
    PageTemplate(id="body", frames=[body_frame], onPage=body_page),
])

toc = TableOfContents()
toc.levelStyles = [S["TOC0"], S["TOC1"]]
toc.dotsMinLevel = 0
toc.tableStyle = TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 1.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
])

story = [NextPageTemplate("body"), PageBreak()]

# ============================================================ ЭКСПРЕСС-ОБЗОР
story += h1("Экспресс-обзор", None)
story.append(P(
    "Проверка сведений о постановлении 2026 года, запрещающем ввоз товаров "
    "в Республике Казахстан. Состояние на 22 октября 2026 года.", "Lead"))

story.append(kpi_row([
    ("4", "Действующих запрета на ввоз"),
    ("3", "Запрета прекратили действие"),
    ("0", "Постановлений Правительства РК о запрете ввоза"),
    ("7", "Проверенных актов о запретах"),
]))
story.append(Spacer(1, 5 * mm))

story.append(P("Сводная картина на 22 октября 2026 года", "H2"))
rows = [
    ["Пшеница", "1001", "Приказ МСХ РК № 273 от 11.07.2026",
     "с 27.07.2026,<br/>6 месяцев", '<font color="#1E7A4C"><b>Действует</b></font>'],
    ["Яблоки свежие", "0808 10", "Приказ и.о. МСХ РК № 326 от 01.09.2026",
     "03.09 — 31.12.2026", '<font color="#1E7A4C"><b>Действует</b></font>'],
    ["Чай, отдельные<br/>наименования", "—", "Постановление ГГСВ РК от 05.01.2026",
     "с 05.01.2026,<br/>срок не установлен", '<font color="#1E7A4C"><b>Действует</b></font>'],
    ["Вейпы, жидкости,<br/>ароматизаторы", "—", "Закон РК № 74-VIII от 19.04.2024",
     "постоянно", '<font color="#1E7A4C"><b>Действует</b></font>'],
    ["Яйца кур свежие", "0407 21", "Приказ МСХ РК № 146 от 17.04.2026",
     "21.04 — 21.10.2026", '<font color="#A5342A"><b>Истёк</b></font>'],
    ["Томаты свежие", "0702", "Приказ МСХ РК № 250 от 22.06.2026",
     "22.06 — 30.06.2026", '<font color="#A5342A"><b>Истёк</b></font>'],
    ["Строительные<br/>материалы", "9 позиций", "Приказ МПС РК № 237 от 15.05.2026",
     "31.05 — 17.10.2026", '<font color="#A5342A"><b>Отменён</b></font>'],
]
story.append(data_table(
    ["Товар", "ТН ВЭД", "Акт", "Период", "Статус"],
    rows,
    [36 * mm, 17 * mm, 58 * mm, 30 * mm, 25 * mm],
    align_center_cols=(1, 4),
))
story.append(Spacer(1, 2 * mm))
story.append(P(
    "МСХ РК — Министерство сельского хозяйства; МПС РК — Министерство промышленности "
    "и строительства; ГГСВ РК — Главный государственный санитарный врач. "
    "Подробные реквизиты — в разделах 3, 4 и 8.", "Small"))

story.append(Spacer(1, 4 * mm))
story.append(callout(
    "ЧТО ИМЕННО УСТАНОВЛЕНО",
    "Постановления Правительства РК, которое в 2026 году вводило бы запрет ввоза товаров, "
    "не обнаружено. Запреты оформлялись приказами министров сельского хозяйства "
    "и промышленности и строительства, а по чаю — постановлением Главного государственного "
    "санитарного врача. Постановления Правительства РК, принятые в 2026 году в связи "
    "с импортом (№ 314 и № 764), касаются изъятий из национального режима в государственных "
    "закупках и запрета ввоза не устанавливают."))

story.append(Spacer(1, 3 * mm))
story.append(P("Три вывода, которые важны для работы", "H2"))
for title, text in [
    ("Форма акта не имеет значения.",
     "Запрет вводится приказом министра, а не постановлением Правительства. "
     "Поиск по слову «постановление» приведёт к пропуску действующего ограничения."),
    ("Запреты действуют и внутри ЕАЭС.",
     "По пшенице, яблокам и яйцам ограничения распространяются на поставки из России, "
     "Беларуси, Кыргызстана и Армении; сертификат СТ-1 не освобождает от запрета."),
    ("Сроки короткие и меняются.",
     "За десять месяцев 2026 года введено, изменено или отменено более десяти мер; "
     "стройматериалы запретили на шесть месяцев, а отменили через четыре с половиной."),
]:
    story.append(Paragraph(
        f'<font color="{NAVY.hexval()}"><b>{title}</b></font> {text}',
        ParagraphStyle("f", parent=S["Body"], leftIndent=12, bulletIndent=1.5, spaceAfter=4.5),
        bulletText="▪"))

story.append(PageBreak())

# ============================================================ TOC page
story.append(Paragraph("СОДЕРЖАНИЕ", ParagraphStyle(
    "TOCHead", fontName="DVS-B", fontSize=10, leading=13, textColor=GOLD,
    spaceAfter=2)))
story.append(Paragraph("Структура документа", ParagraphStyle(
    "TOCSub", fontName="SER-B", fontSize=17, leading=22, textColor=NAVY,
    spaceAfter=4)))
story.append(HRFlowable(width="100%", thickness=1.1, color=GOLD, spaceAfter=10))
story.append(toc)

story.append(Spacer(1, 8 * mm))
story.append(Spacer(1, 6 * mm))
story.append(callout(
    "КАК ЧИТАТЬ ДОКУМЕНТ",
    "Справка отвечает на два вопроса: существует ли постановление 2026 года, запрещающее "
    "ввоз товаров, и какие запреты фактически действуют на 22 октября 2026 года. "
    "Статусы обозначены цветом: зелёный — действует, красный — прекратил действие. "
    "Реквизиты актов приведены по официальным публикациям.",
))
story.append(PageBreak())

# ============================================================ 1. Резюме
story += h1("Резюме проверки", 1)

story.append(P(
    "Предмет проверки — сведения о постановлении 2026 года, устанавливающем в Республике "
    "Казахстан запрет на ввоз товаров. Проверка проведена по состоянию на 22 октября "
    "2026 года по официальным текстам нормативных правовых актов, данным реестров "
    "и сообщениям уполномоченных органов.", "Lead"))

story.append(P(
    "Постановление Правительства Республики Казахстан, которое в 2026 году вводило бы запрет "
    "на ввоз товаров как таковой, в открытых официальных источниках <b>не обнаружено</b>. "
    "Запреты на ввоз в 2026 году устанавливались приказами министров — сельского хозяйства "
    "и промышленности и строительства. Единственный выявленный акт в форме постановления — "
    "постановление Главного государственного санитарного врача РК от 5 января 2026 года — "
    "касается только отдельных наименований чая и не носит общего характера."))

story.append(P(
    "Постановления Правительства РК, принятые в 2026 году в связи с импортом, регулируют иные "
    "инструменты: изъятия из национального режима при государственных закупках "
    "(№ 314 от 23 апреля 2026 года, № 764 от 26 августа 2026 года), налоговое "
    "администрирование импорта и порядок применения НДС. Они не являются запретом ввоза "
    "и не ограничивают перемещение товаров через границу."))

story.append(Spacer(1, 2 * mm))
story.append(P("Ключевые выводы", "H2"))

findings = [
    ("Единого «постановления о запрете ввоза» нет.",
     "В 2026 году запреты оформлялись приказами профильных министров — это подзаконные "
     "нормативные правовые акты, регистрируемые в Минюсте и официально публикуемые."),
    ("Действуют четыре запрета.",
     "Пшеница (приказ № 273), яблоки (приказ № 326), отдельные наименования чая "
     "(постановление Главного государственного санитарного врача) и постоянный запрет "
     "на ввоз вейпов (Закон № 74-VIII)."),
    ("Три запрета прекратили действие.",
     "Яйца кур свежих — срок истёк 21 октября 2026 года; томаты — 30 июня 2026 года; "
     "строительные материалы — запрет отменён с 17 октября 2026 года."),
    ("Запреты распространяются и на ЕАЭС.",
     "По пшенице, яблокам и яйцам ограничения действуют не только для третьих стран, "
     "но и для государств — членов Евразийского экономического союза. Это отличает их "
     "от классических защитных мер."),
    ("Форма запрета не важна для правоприменения.",
     "Для импортёра юридически значим не уровень акта, а код ТН ВЭД, направление ввоза, "
     "вид транспорта и дата ввоза. Проверять нужно конкретный приказ, а не наличие "
     "«постановления»."),
]
for title, text in findings:
    story.append(Paragraph(
        f'<font color="{NAVY.hexval()}"><b>{title}</b></font> {text}',
        ParagraphStyle("f", parent=S["Body"], leftIndent=12, bulletIndent=1.5, spaceAfter=4.5),
        bulletText="▪"))

story.append(Spacer(1, 3 * mm))
story.append(P(
    "<b>Итоговая формулировка.</b> Проверка не подтвердила наличие постановления "
    "Правительства Республики Казахстан 2026 года, которым вводился бы запрет ввоза "
    "товаров. Действующие ограничения носят отраслевой характер, устанавливаются "
    "приказами министров и касаются конкретных товарных позиций; проверять их следует "
    "по товару, коду ТН ВЭД и дате ввоза, а не по форме акта.", "Body"))
story.append(Spacer(1, 2 * mm))
story.append(callout(
    "ОГРАНИЧЕНИЕ ВЫВОДА",
    "Вывод сформулирован по открытым официальным источникам по состоянию на 22.10.2026. "
    "Если проверяемое постановление имеет конкретные реквизиты (номер, дату, орган), "
    "его следует сверить адресно в ИПС «Әділет» или Эталонном контрольном банке НПА: "
    "практика 2026 года показывает, что ограничения меняются в течение нескольких недель.",
))
story.append(PageBreak())

# ============================================================ 2. Правовая рамка
story += h1("Правовая рамка и методика проверки", 2)

story.append(P(
    "Запрет на ввоз товара — мера нетарифного регулирования внешнеторговой деятельности. "
    "В Казахстане такие меры вводятся по решению Межведомственной комиссии по вопросам "
    "внешнеторговой политики и оформляются приказами уполномоченных министерств. "
    "Приказ министра является нормативным правовым актом: он проходит государственную "
    "регистрацию в Министерстве юстиции, официально публикуется и только после этого "
    "вступает в силу."))

story.append(P(
    "Именно поэтому запрет 2026 года не оформлялся постановлением Правительства: "
    "для оперативных ограничений внешней торговли достаточно приказа профильного министра. "
    "Постановления Правительства применяются для более общих вопросов — национального режима "
    "в государственных закупках, налоговых правил, тарифной политики."))

story.append(P("2.1. Уровни регулирования", "H2"))
rows = [
    ["Закон", "Закон РК «О регулировании торговой деятельности», "
              "Предпринимательский кодекс, Договор о ЕАЭС",
     "Устанавливает основания и пределы ограничений; прямых запретов на товары не содержит"],
    ["Постановление Правительства", "Постановления Правительства РК",
     "Регулирует национальный режим, налоги, тарифы; запрет ввоза товара как таковой "
     "в 2026 году не устанавливал"],
    ["Приказ министра", "Приказы МСХ РК, МПС РК, Минфина РК",
     "Рабочий инструмент введения запретов и ограничений в 2026 году"],
    ["Постановление Главного государственного санитарного врача", "Постановление ГГСВ РК от 05.01.2026",
     "Временные санитарные меры в отношении конкретных наименований чая"],
]
story.append(data_table(
    ["Уровень", "Акты", "Роль в регулировании ввоза"],
    rows, [39 * mm, 55 * mm, 72 * mm]))
story.append(Spacer(1, 3 * mm))

story.append(P("2.2. Как вводится запрет", "H2"))
for i, t in enumerate([
    "Межведомственная комиссия по вопросам внешнеторговой политики принимает решение "
    "о введении временного запрета.",
    "Профильное министерство готовит проект приказа и выносит его на публичное обсуждение "
    "на портале «Открытые НПА».",
    "Приказ регистрируется в Министерстве юстиции и официально публикуется.",
    "Запрет вступает в силу с даты, указанной в приказе; срок обычно составляет "
    "от одного до шести месяцев.",
], 1):
    story.append(numbered(i, t))

story.append(P("2.3. Что проверено", "H2"))
story.append(P(
    "Проверены ИПС «Әділет» и Эталонный контрольный банк НПА, портал «Открытые НПА», "
    "официальные публикации и сообщения Министерства сельского хозяйства, Министерства "
    "промышленности и строительства, Комитета государственных доходов, а также профильные "
    "отраслевые издания за период с 1 января по 22 октября 2026 года. Отдельно проверено "
    "наличие постановлений Правительства РК, которые могли бы быть приняты за запрет ввоза."))
story.append(Spacer(1, 2 * mm))
story.append(callout(
    "ТЕРМИНОЛОГИЧЕСКОЕ РАЗЛИЧЕНИЕ",
    "Запрет ввоза (эмбарго) — полный запрет перемещения товара через границу. "
    "Пошлина, квота, лицензирование, изъятие из национального режима в госзакупках, "
    "ветеринарное ограничение по региону и критерии предпринимательской деятельности — "
    "это разные инструменты. Они могут ограничивать поставки, но не являются запретом ввоза "
    "в юридическом смысле.",
))
story.append(PageBreak())

# ============================================================ 3. Действующие
story += h1("Запреты, действующие на 22 октября 2026 года", 3)

story.append(P(
    "На дату подготовки справки действуют четыре запрета: три временных товарных "
    "и один постоянный. Ниже приведены их карточки с реквизитами, сферой действия "
    "и исключениями."))

# --- 3.1 wheat
story.append(KeepTogether([
    h2("3.1. Пшеница"),
    status("Действует", GREEN, "введён с 27.07.2026, срок — 6 месяцев"),
    card([
        ("Акт", "Приказ Министра сельского хозяйства РК от 11 июля 2026 года № 273 "
                "«О введении запрета на ввоз пшеницы на территорию Республики Казахстан "
                "автомобильным, водным и железнодорожным транспортом»"),
        ("Товар", "Пшеница, код ТН ВЭД ЕАЭС 1001"),
        ("Направление ввоза", "Из третьих стран и из государств — членов ЕАЭС"),
        ("Виды транспорта", "Автомобильный, водный, железнодорожный"),
        ("Исключения", "Железнодорожные поставки в адрес птицеводческих и зерноперерабатывающих "
                       "предприятий, лицензированных элеваторов и АО «НК «Продовольственная "
                       "контрактная корпорация»; транзит железнодорожным транспортом; перевозки "
                       "между государствами — членами ЕАЭС через территорию РК"),
        ("Особое условие", "Пшеница, ввезённая для птицеводческих и зерноперерабатывающих "
                           "предприятий, не подлежит реализации на внутреннем и внешнем рынках"),
    ]),
]))
story.append(Spacer(1, 1.5 * mm))
story.append(P(
    "<b>Практическое значение.</b> Запрет затрагивает основной канал поставок — российскую "
    "пшеницу. Разрешённая схема остаётся только для железнодорожных поставок ограниченному "
    "кругу получателей; автомобильные и водные перевозки закрыты полностью. Нарушение условия "
    "о запрете перепродажи создаёт риск для получателя и для всей цепочки поставки.", "Body"))
story.append(P(
    "<b>Динамика.</b> В сентябре 2026 года обсуждался проект изменений, который оставлял "
    "железнодорожное исключение только для АО «НК «Продовольственная контрактная корпорация». "
    "По состоянию на дату справки официально подтверждённых сведений о вступлении этих "
    "изменений в силу нет; перед сделкой необходимо проверить действующую редакцию приказа "
    "в ИПС «Әділет».", "Body"))

# --- 3.2 apples
story.append(KeepTogether([
    h2("3.2. Яблоки"),
    status("Действует", GREEN, "с 03.09.2026 по 31.12.2026 включительно"),
    card([
        ("Акт", "Приказ и.о. Министра сельского хозяйства РК от 1 сентября 2026 года № 326 "
                "«О введении запрета на ввоз яблок на территорию Республики Казахстан»"),
        ("Товар", "Яблоки свежие, код ТН ВЭД ЕАЭС 0808 10"),
        ("Направление ввоза", "Из третьих стран и из государств — членов ЕАЭС"),
        ("Виды транспорта", "Все виды транспорта"),
        ("Исключения", "Транзит через территорию РК, если местом назначения не является Казахстан; "
                       "товары, помещённые под процедуру экспорта в стране отправления до 3 сентября "
                       "2026 года, при наличии экспортной и транспортной деклараций; товары, "
                       "фактически ввезённые в Казахстан до 3 сентября 2026 года"),
    ]),
]))
story.append(Spacer(1, 1.5 * mm))
story.append(P(
    "<b>Практическое значение.</b> Запрет действует почти четыре месяца — до конца 2026 года "
    "и охватывает поставки из ЕАЭС, включая российские и киргизские яблоки. Для товара, "
    "отгруженного до 3 сентября, критически важны документы, подтверждающие дату отправки "
    "или фактического ввоза: без них таможенный орган не применит переходное исключение.", "Body"))

# --- 3.3 tea
story.append(KeepTogether([
    h2("3.3. Чай: отдельные наименования"),
    status("Действует", GREEN, "с 05.01.2026, срок не установлен"),
    card([
        ("Акт", "Постановление Главного государственного санитарного врача РК "
                "от 5 января 2026 года о введении временных санитарных мер"),
        ("Товар", "Отдельные наименования чёрного чая, не соответствующие требованиям "
                  "ТР ТС 021/2011, ТР ТС 029/2012 и ТР ТС 022/2011"),
        ("Запрет", "Запрет ввоза и реализации конкретных наименований (брендов) чая"),
        ("Основание", "Выявлены пищевые красители Е110, Е102 и Е124, использование которых "
                      "в чае не допускается, а также недействительные адреса производства "
                      "и расфасовки"),
        ("Перечень", "«Апамның шәйі Premium gold», «Al-Hayat Golg», «БАЛҚИЯ Premium Gold», "
                     "«Sultan Suleyman», «Pakistan tea», «Aje Onim», «Al-Jannat Premium», "
                     "«Alfarah» (отдельные партии и производители)"),
    ]),
]))
story.append(Spacer(1, 1.5 * mm))
story.append(P(
    "<b>Практическое значение.</b> Это единственный в 2026 году запрет, оформленный "
    "постановлением, однако он принят не Правительством, а Главным государственным "
    "санитарным врачом. Запрет не является товарным эмбарго: он касается конкретных "
    "наименований и обусловлен безопасностью продукции. Для импортёра чая риск связан "
    "с идентификацией бренда и производителя, а не с кодом ТН ВЭД.", "Body"))

# --- 3.4 vapes
story.append(KeepTogether([
    h2("3.4. Вейпы и электронные системы потребления"),
    status("Действует", GREEN, "с 20.06.2024, постоянный запрет"),
    card([
        ("Акт", "Закон РК от 19 апреля 2024 года № 74-VIII «О внесении изменений и дополнений "
                "в некоторые законодательные акты Республики Казахстан по вопросам "
                "здравоохранения»"),
        ("Товар", "Некурительные табачные изделия, электронные системы потребления (вейпы), "
                  "ароматизаторы и жидкости для них"),
        ("Запрет", "Запрещены ввоз, производство, продажа и распространение; запрет "
                   "распространяется и на ввоз для личного пользования"),
        ("Ответственность", "Статья 301-1 Уголовного кодекса РК: штраф до 2 000 МРП, "
                            "ограничение или лишение свободы до 2 лет; при повторности "
                            "или группой лиц — до 5 лет"),
    ]),
]))
story.append(Spacer(1, 1.5 * mm))
story.append(P(
    "<b>Практическое значение.</b> Запрет действует с 2024 года, но остаётся самым "
    "жёстким по последствиям: ввоз даже одного устройства для личного пользования "
    "образует состав уголовного правонарушения. В 2026 году пограничные и экономические "
    "органы продолжали изымать крупные партии такой продукции.", "Body"))

story.append(Spacer(1, 3 * mm))
rows = [
    ["Товар и код", "Пшеница, 1001", "Яблоки, 0808 10",
     "Отдельные наименования чая", "Вейпы и жидкости"],
    ["Страны", "Третьи страны и ЕАЭС", "Третьи страны и ЕАЭС",
     "Любое происхождение", "Любое происхождение"],
    ["Транспорт", "Авто, вода, ж/д", "Все виды", "Все виды", "Все виды"],
    ["Разрешено", "Ж/д — элеваторы, переработчики, птицеводы, Продкорпорация; транзит",
     "Транзит; отгрузки и ввоз до 03.09.2026", "Наименования вне перечня",
     "Ничего, включая личное пользование"],
    ["Срок", "6 месяцев с 27.07.2026", "До 31.12.2026", "Бессрочно, до отмены", "Постоянно"],
    ["Ответственность", "Запрет ввоза, возврат товара", "Запрет ввоза, возврат товара",
     "Изъятие из оборота", "Уголовная, ст. 301-1 УК РК"],
]
story.append(PageBreak())
story.append(P("3.5. Сводное сравнение действующих запретов", "H2"))
story.append(P(
    "Таблица сводит четыре действующих запрета по шести параметрам, которые проверяются "
    "при подготовке поставки. Различия между ними существенны: одинаковый статус "
    "«действует» не означает одинакового охвата."))
story.append(data_table(
    ["Параметр", "Пшеница", "Яблоки", "Чай", "Вейпы"],
    rows, [31 * mm, 35 * mm, 33 * mm, 33 * mm, 34 * mm]))
story.append(Spacer(1, 3 * mm))
story.append(callout(
    "КАК ПОЛЬЗОВАТЬСЯ СРАВНЕНИЕМ",
    "Пшеница и яблоки закрыты для ввоза почти полностью: исключения узкие и требуют "
    "подтверждающих документов. Чай ограничен не по коду, а по конкретным наименованиям, "
    "поэтому проверять нужно бренд и производителя. Вейпы запрещены полностью, включая "
    "ввоз для личного пользования, и влекут уголовную ответственность."))
story.append(Spacer(1, 3 * mm))
story.append(callout(
    "ЧТО ПРОВЕРЯТЬ В ПЕРВУЮ ОЧЕРЕДЬ",
    "1) Подпадает ли товар под запрет по коду и наименованию. 2) Разрешён ли ввоз "
    "из страны происхождения. 3) Допустим ли выбранный вид транспорта. 4) Есть ли "
    "основание для исключения и документы по нему. 5) Не истёк ли срок действия акта "
    "на дату ввоза.",
    accent=NAVY2,
    bg=LIGHT2,
))

story.append(Spacer(1, 4 * mm))
story.append(P("3.6. Если товар подпадает под запрет", "H2"))
story.append(P(
    "Порядок действий зависит от того, состоялась ли поставка. В обоих случаях "
    "первым шагом является сверка реквизитов акта и даты ввоза."))
for i, t in enumerate([
    "Приостановить отгрузку и проверить действующую редакцию приказа в ИПС «Әділет» "
    "на дату планируемого ввоза.",
    "Проверить, подпадает ли товар под исключение: получатель, вид транспорта, "
    "дата отгрузки или фактического ввоза.",
    "Подготовить документы, подтверждающие право на исключение: контракт, "
    "транспортные и экспортные декларации, документы о статусе получателя.",
    "Если ввоз уже состоялся в период действия запрета — оценить риски и обратиться "
    "к юристу до подачи корректирующих документов.",
], 1):
    story.append(numbered(i, t))

story.append(PageBreak())

# ============================================================ 4. Прекратившие действие
story += h1("Запреты, прекратившие действие в 2026 году", 4)

story.append(P(
    "Три запрета, действовавшие в 2026 году, к дате подготовки справки прекратили действие. "
    "Их важно учитывать при проверке периода поставки и при ретроспективном комплаенсе: "
    "поставка, законная в мае, может оказаться нарушением в августе, и наоборот."))
story.append(Spacer(1, 1 * mm))
story.append(callout(
    "ЧТО ЭТО ЗНАЧИТ ДЛЯ ДОКУМЕНТОВ",
    "Документы по поставке оцениваются по редакции акта, действовавшей на дату ввоза. "
    "Отмена запрета не превращает ранее незаконный ввоз в законный, а истечение срока "
    "не создаёт оснований для возврата уплаченных платежей."))
story.append(Spacer(1, 2 * mm))

# eggs
story.append(KeepTogether([
    h2("4.1. Яйца кур свежие"),
    status("Прекратил действие", RED, "срок истёк 21.10.2026"),
    card([
        ("Акт", "Приказ Министра сельского хозяйства РК от 17 апреля 2026 года № 146"),
        ("Товар", "Яйца кур свежие, код ТН ВЭД ЕАЭС 0407 21"),
        ("Период", "С 21 апреля 2026 года, срок — шесть месяцев; с 21 октября 2026 года "
                   "акт не подлежит применению"),
        ("Сфера", "Ввоз всеми видами транспорта из третьих стран и из государств — членов ЕАЭС"),
        ("Исключения", "Транзит через территорию РК; перемещение между государствами — "
                       "членами ЕАЭС через территорию РК"),
    ]),
]))
story.append(Spacer(1, 1.5 * mm))
story.append(P(
    "Сведений о продлении запрета на дату подготовки справки в открытых источниках "
    "не обнаружено. В то же время Минсельхоз публично обсуждал новый запрет на весенне-летний "
    "период, поэтому вопрос требует мониторинга.", "Body"))

# tomatoes
story.append(KeepTogether([
    h2("4.2. Томаты свежие или охлаждённые"),
    status("Прекратил действие", RED, "истёк 30.06.2026"),
    card([
        ("Акт", "Приказ Министра сельского хозяйства РК от 22 июня 2026 года № 250 "
                "«О некоторых вопросах ввоза томатов на территорию Республики Казахстан»"),
        ("Товар", "Томаты свежие или охлаждённые, код ТН ВЭД ЕАЭС 0702"),
        ("Период", "С 22 июня 2026 года до 30 июня 2026 года"),
        ("Сфера", "Ввоз всеми видами транспорта из третьих стран"),
        ("Исключения", "Ввоз из государств — членов ЕАЭС; транзит; перемещение между "
                       "государствами — членами ЕАЭС через территорию РК"),
    ]),
]))
story.append(Spacer(1, 1.5 * mm))
story.append(P(
    "Запрет был краткосрочным и не затронул поставки из ЕАЭС. На дату справки он "
    "не действует; сведений о продлении не обнаружено.", "Body"))

# construction
story.append(KeepTogether([
    h2("4.3. Строительные материалы"),
    status("Отменён", RED, "отменён с 17.10.2026 приказом № 499"),
    card([
        ("Акт", "Приказ Министра промышленности и строительства РК от 15 мая 2026 года № 237 "
                "(с изменениями от 3 августа 2026 года № 386)"),
        ("Товары", "Цемент (2523 29, 2523 90), сухие строительные смеси и растворы (3824 50 900 0), "
                   "брусчатка и плиты для мощения (6801 00), изделия из камня и гранита "
                   "(6802 23, 6802 93 100 0, 6802 93 900 0), гипсовые плиты (6809 11 000 0), "
                   "листовое стекло (7003, 7004, 7005)"),
        ("Период", "С 31 мая 2026 года, срок — шесть месяцев"),
        ("Сфера", "Ввоз из третьих стран всеми видами транспорта"),
        ("Отмена", "Приказ Министра промышленности и строительства РК от 5 октября 2026 года № 499; "
                   "вступил в силу 17 октября 2026 года"),
    ]),
]))
story.append(Spacer(1, 1.5 * mm))
story.append(P(
    "<b>Практическое значение.</b> Запрет отменён досрочно, до истечения шестимесячного срока. "
    "Поставки стройматериалов из третьих стран возобновлены с 17 октября 2026 года. "
    "При этом сохраняются иные меры регулирования (технические регламенты, пошлины, "
    "сертификация), которые не отменялись.", "Body"))


# ============================================================ 5. Смежные ограничения
story.append(CondPageBreak(110 * mm))
story += h1("Ограничения, которые не являются запретом ввоза", 5)

story.append(P(
    "В 2026 году принят ряд актов, которые в публикациях и деловой переписке иногда "
    "называют «запретом ввоза». Юридически они регулируют иные отношения и не образуют "
    "запрета на перемещение товара через границу."))

rows = [
    ["Изъятия из национального режима в государственных закупках",
     "Постановления Правительства РК № 314 от 23.04.2026 и № 764 от 26.08.2026",
     "Ограничивают участие иностранных поставщиков и иностранных товаров в госзакупках. "
     "Частный импорт и коммерческие поставки не затрагивают"],
    ["Ветеринарные и фитосанитарные ограничения",
     "Решения Комитета ветеринарного контроля и надзора МСХ РК; ограничения "
     "от 11.02.2026 и 19.09.2026",
     "Действуют по регионам и видам продукции, меняются оперативно; не являются "
     "запретом на товар в целом"],
    ["Условия ввоза автомобилей",
     "Приказы МПС РК 2026 года; правила оформления ЭПТС и уплаты утильсбора",
     "Ограничивают возраст автомобиля и порядок оформления, но не запрещают ввоз "
     "как таковой"],
    ["Налоговые и таможенные правила",
     "Приказ Минфина РК № 690 от 11.11.2025 (с 01.01.2026); правила электронной торговли",
     "Определяют критерии предпринимательского ввоза (360 МРП) и порог беспошлинного "
     "ввоза, но не запрещают поставки"],
    ["Разрешительный порядок вывоза",
     "Совместный приказ пяти ведомств от 20.11.2025",
     "Касается экспорта отдельных товаров, а не ввоза"],
]
story.append(data_table(
    ["Инструмент", "Акты", "Суть и отличие от запрета"],
    rows, [42 * mm, 52 * mm, 72 * mm], small=True))
story.append(Spacer(1, 3 * mm))

story.append(P("5.1. Почему это важно", "H2"))
story.append(P(
    "Для целей комплаенса недостаточно проверить, существует ли «постановление о запрете». "
    "Нужно установить, каким актом регулируется конкретный товар, и определить природу "
    "ограничения: запрет ввоза, пошлина, квота, лицензирование, санитарная мера или "
    "изъятие из национального режима. От этого зависят документы, которые нужно подготовить, "
    "и риск ответственности."))
story.append(callout(
    "ПРИМЕР",
    "Постановление Правительства РК № 314 от 23 апреля 2026 года не запрещает ввоз "
    "иностранных товаров. Оно устанавливает изъятие из национального режима при "
    "государственных закупках: иностранный товар можно ввезти, но его нельзя поставить "
    "по отдельным государственным закупкам. Это ограничение доступа к закупкам, "
    "а не запрет импорта."))
story.append(PageBreak())

# ============================================================ 6. Хронология
story += h1("Хронология 2026 года", 6)
story.append(P(
    "Ниже сведены ключевые события, влияющие на запреты ввоза, в хронологическом порядке. "
    "Даты вступления в силу указаны по официальным публикациям."))

rows = [
    ["05.01.2026", "Введены временные санитарные меры: запрет ввоза и реализации отдельных "
                   "наименований чая", "Постановление ГГСВ РК"],
    ["11.02.2026", "Введены временные ограничения на ввоз скота и кормовой продукции "
                   "из ряда регионов РФ", "Решение Комитета ветеринарного контроля"],
    ["21.03.2026", "Ограничен ввоз зерновых культур и кормов из РФ (оперативное решение, "
                   "не зарегистрированный НПА)", "Документ КГИ МСХ РК"],
    ["17.04.2026", "Подписан приказ о запрете ввоза яиц кур свежих на шесть месяцев",
     "Приказ МСХ РК № 146"],
    ["23.04.2026", "Установлены изъятия из национального режима в государственных закупках",
     "Постановление Правительства РК № 314"],
    ["15.05.2026", "Введён запрет ввоза отдельных строительных материалов из третьих стран",
     "Приказ МПС РК № 237"],
    ["31.05.2026", "Запрет на ввоз строительных материалов вступил в силу", "Приказ № 237"],
    ["22.06.2026", "Введён краткосрочный запрет ввоза томатов из третьих стран",
     "Приказ МСХ РК № 250"],
    ["11.07.2026", "Введён шестимесячный запрет ввоза пшеницы", "Приказ МСХ РК № 273"],
    ["27.07.2026", "Запрет на ввоз пшеницы вступил в силу", "Приказ № 273"],
    ["03.08.2026", "Перечень стройматериалов дополнен", "Приказ МПС РК № 386"],
    ["26.08.2026", "Изъятие из национального режима для цифровых товаров и услуг",
     "Постановление Правительства РК № 764"],
    ["01.09.2026", "Подписан приказ о запрете ввоза яблок", "Приказ и.о. МСХ РК № 326"],
    ["03.09.2026", "Запрет на ввоз яблок вступил в силу", "Приказ № 326"],
    ["19.09.2026", "Введены ограничения на ввоз животноводческой продукции из четырёх "
                   "регионов РФ", "Решение Комитета ветеринарного контроля"],
    ["05.10.2026", "Отменён запрет на ввоз строительных материалов", "Приказ МПС РК № 499"],
    ["17.10.2026", "Отмена запрета на стройматериалы вступила в силу", "Приказ № 499"],
    ["21.10.2026", "Истёк срок запрета на ввоз яиц кур свежих", "Приказ МСХ РК № 146"],
]
story.append(data_table(
    ["Дата", "Событие", "Документ"],
    rows, [21 * mm, 95 * mm, 50 * mm], small=True))
story.append(Spacer(1, 2 * mm))
story.append(P(
    "Хронология показывает высокую динамику: за десять месяцев 2026 года введено, изменено "
    "или отменено более десяти ограничительных мер. Это подтверждает необходимость "
    "проверки действующей редакции акта перед каждой поставкой.", "Small"))

# ============================================================ 7. Рекомендации
story.append(CondPageBreak(120 * mm))
story += h1("Практические выводы для импортёра", 7)

story.append(P(
    "Ниже — алгоритм проверки, который учитывает выявленную специфику 2026 года."))

recs = [
    ("Проверяйте приказ, а не «постановление».",
     "Основной массив запретов оформлен приказами МСХ и МПС. Поиск по слову "
     "«постановление» приведёт к пропуску действующего ограничения."),
    ("Идентифицируйте товар по коду ТН ВЭД и описанию.",
     "Запреты сформулированы одновременно по коду и по наименованию. Для чая, вейпов "
     "и стройматериалов код недостаточен — нужна проверка бренда, состава или "
     "товарной позиции."),
    ("Учитывайте происхождение товара.",
     "По пшенице, яблокам и яйцам запрет распространяется и на товары из ЕАЭС. "
     "Сертификат СТ-1 или российское происхождение не освобождают от ограничения."),
    ("Проверяйте вид транспорта и маршрут.",
     "Для пшеницы разрешены только железнодорожные поставки ограниченному кругу "
     "получателей; автомобильные и водные перевозки запрещены. Транзит через Казахстан "
     "в большинстве случаев не ограничен."),
    ("Фиксируйте дату отгрузки и ввоза.",
     "Переходные исключения по яблокам зависят от даты помещения товара под экспортную "
     "процедуру или фактического ввоза. Сохраняйте экспортные, товарные и транспортные "
     "документы."),
    ("Учитывайте условие о запрете перепродажи.",
     "Пшеница, ввезённая для птицеводческих и зерноперерабатывающих предприятий, "
     "не может реализовываться на внутреннем и внешнем рынках. Это самостоятельный "
     "риск для получателя и покупателя."),
    ("Проверяйте актуальность перед каждой поставкой.",
     "В 2026 году запреты вводились и отменялись в течение нескольких недель. "
     "Действующую редакцию следует проверять в ИПС «Әділет» и на портале «Открытые НПА» "
     "непосредственно перед сделкой."),
    ("Для вейпов действует особый режим.",
     "Ввоз даже одного устройства для личного пользования образует состав уголовного "
     "правонарушения по статье 301-1 УК РК. Коммерческие поставки исключены полностью."),
]
for i, (title, text) in enumerate(recs, 1):
    story.append(Paragraph(
        f'<font color="{NAVY.hexval()}"><b>{title}</b></font> {text}',
        ParagraphStyle("rec", parent=S["Body"], leftIndent=14, bulletIndent=0, spaceAfter=5),
        bulletText=f"{i}."))

story.append(Spacer(1, 2 * mm))
story.append(callout(
    "ЧЕК-ЛИСТ ПЕРЕД ПОСТАВКОЙ",
    "1) Код ТН ВЭД и точное наименование товара.  2) Страна происхождения и страна "
    "отправления.  3) Вид транспорта и маршрут (включая транзит).  4) Дата отгрузки "
    "и дата фактического ввоза.  5) Действующая редакция приказа и срок его действия.  "
    "6) Исключения и документы, подтверждающие право на них.  7) Ограничения по получателю "
    "товара и условиям последующей реализации.",
))

# ============================================================ Приложение А
story.append(CondPageBreak(100 * mm))
story += h1("Приложение А. Карточка проверки", None)
story.append(P(
    "Формализованный результат проверки сведений о постановлении 2026 года, "
    "запрещающем ввоз товаров."))

app_rows = [
    ["Проверяемый вопрос", "Наличие постановления 2026 года, устанавливающего запрет "
                           "на ввоз товаров в Республике Казахстан"],
    ["Период проверки", "1 января — 22 октября 2026 года"],
    ["Проверенные ресурсы", "ИПС «Әділет»; Эталонный контрольный банк НПА; портал "
                            "«Открытые НПА»; официальные сайты МСХ, МПС, КГД; "
                            "официальные публикации и сообщения государственных органов"],
    ["Постановления Правительства РК", "Не выявлено постановления, вводящего запрет ввоза "
                                       "товаров как таковой"],
    ["Акты в форме постановления", "Постановление Главного государственного санитарного "
                                   "врача РК от 05.01.2026 — только отдельные наименования чая"],
    ["Выявленные запреты", "7 актов: 4 действующих, 3 прекративших действие"],
    ["Действующие запреты", "Пшеница (1001); яблоки (0808 10); отдельные наименования чая; "
                            "вейпы и электронные системы потребления"],
    ["Прекратившие действие", "Яйца кур свежих (0407 21) — 21.10.2026; томаты (0702) — "
                              "30.06.2026; строительные материалы — 17.10.2026"],
    ["Итог", "Сведения о едином постановлении Правительства РК о запрете ввоза товаров "
             "не подтверждаются. Действуют отраслевые приказы министров и санитарное "
             "постановление по чаю"],
]
t = Table([[Paragraph(k, S["CardLabel"]), Paragraph(v, S["CardValue"])] for k, v in app_rows],
          colWidths=[48 * mm, CONTENT_W - 48 * mm], hAlign="LEFT")
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), LIGHT2),
    ("GRID", (0, 0), (-1, -1), 0.35, LINE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Spacer(1, 4 * mm))
story.append(callout(
    "МЕТОДОЛОГИЧЕСКАЯ ОГОВОРКА",
    "Проверка проведена по открытым источникам. Официальные тексты отдельных приказов "
    "на дату подготовки справки были доступны в изложении уполномоченных органов "
    "и отраслевых изданий; перед принятием юридически значимого решения рекомендуется "
    "запросить заверенную копию акта или сверить его в ИПС «Әділет».",
    accent=AMBER,
    bg=HexColor("#FAF6EC"),
))

story.append(Spacer(1, 7 * mm))
story.append(P("Периоды действия запретов в 2026 году", "H2"))
story.append(P(
    "Схема показывает, как распределялись периоды действия ограничений в течение года. "
    "Серым отмечены меры, прекратившие действие, зелёным — действующие на 22 октября "
    "2026 года, золотым — бессрочная санитарная мера по чаю.", "Small"))
story.append(Spacer(1, 2 * mm))
story.append(TimelineDiagram(CONTENT_W))

# ============================================================ 8. Источники
story.append(CondPageBreak(150 * mm))
story += h1("Источники", 8)
story.append(P(
    "Дата обращения ко всем источникам — 22 октября 2026 года. Ссылки приведены "
    "в сокращённом виде; полные адреса доступны по указанным доменам и идентификаторам "
    "публикаций."))

sources = [
    ("ИПС «Әділет» — информационно-правовая система нормативных правовых актов РК",
     "adilet.zan.kz"),
    ("Приказ Министра сельского хозяйства РК от 11.07.2026 № 273; карточка документа",
     "zan.gov.kz/client/#!/doc/227657/rus"),
    ("Запрет на ввоз пшеницы: разъяснение исключений",
     "inform.kz/ru/pshenitsu-zapretili-vvozit-vkazahstan-kakie-isklyucheniya-predusmotreni-d7e9db07"),
    ("Приказ Министра сельского хозяйства РК от 17.04.2026 № 146 (текст и статус)",
     "cdb.kz; alta.ru/tamdoc/26kz0146"),
    ("Приказ Министра сельского хозяйства РК от 22.06.2026 № 250",
     "zakon.mybuh.kz/rus/docs/v2600039026"),
    ("Запрет на ввоз яблок с 3 сентября 2026 года",
     "zakon.kz/pravo/6530447; ulysmedia.kz/news/80098"),
    ("Приказ Министра промышленности и строительства РК от 15.05.2026 № 237; перечень товаров",
     "mybuh.kz/news/vveden-zapret-na-vvoz-nekotorykh-stroitelnykh-materialov-v-kazakhstan"),
    ("Отмена запрета на ввоз строительных материалов с 17 октября 2026 года",
     "tengrinews.kz/kazakhstan_news/...-611289; 24.kz/ru/news/economyc/800874"),
    ("Постановление Главного государственного санитарного врача РК от 05.01.2026; перечень чая",
     "inform.kz/ru/zapret-na-vvoznekotorih-naimenovaniy-chaya-ustanovili-v-kazahstane-9c5e2d"),
    ("Закон РК от 19.04.2024 № 74-VIII; статья 301-1 Уголовного кодекса РК",
     "kst.kgd.gov.kz; zakon.kz/obshestvo/6438723"),
    ("Постановление Правительства РК от 23.04.2026 № 314 об изъятии из национального режима",
     "adilet.zan.kz/rus/docs/P2600000314"),
    ("Постановление Правительства РК от 26.08.2026 № 764 об изъятии из национального режима",
     "inbusiness.kz/ru/last/v-kazahstane-vveli-novoe-ogranichenie-dlya-inostrannyh-tovarov-v-goszakupkah"),
    ("Приказ Министра финансов РК от 11.11.2025 № 690 о критериях предпринимательского ввоза",
     "tsnik.kz/news/vvoz-tovarov-iz-eaes-s-2026-goda-novye-pravila-i-limity-v-kazakhstane"),
    ("Ветеринарные ограничения и их смягчение (сентябрь — октябрь 2026 года)",
     "ulysmedia.kz/news/83023; regtv.kz/2026/10/16"),
    ("Обзор запретов и ограничений по импорту и экспорту в РК — 2026",
     "gz.mcfr.kz/article/553"),
    ("Публикации о ходе введения запретов: Kommersant, Kapital.kz, Zakon.kz, Kursiv.kz",
     "kommersant.ru; kapital.kz; zakon.kz; kz.kursiv.media"),
]
for i, (title, url) in enumerate(sources, 1):
    story.append(Paragraph(f"{i}. {title}", S["Src"]))
    story.append(Paragraph(url, S["SrcUrl"]))

story.append(Spacer(1, 5 * mm))
story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceAfter=5))
story.append(P(
    "<b>Оговорка.</b> Настоящий документ подготовлен в информационно-аналитических целях "
    "и не является юридическим заключением, консультацией или официальным разъяснением "
    "государственного органа. Выводы основаны на открытых источниках по состоянию "
    "на 22 октября 2026 года. Нормативные правовые акты могут быть изменены, дополнены "
    "или отменены; перед принятием решений рекомендуется проверить действующую редакцию "
    "акта в ИПС «Әділет» и при необходимости обратиться к квалифицированному юристу.", "SmallJ"))
story.append(Spacer(1, 3 * mm))
story.append(P(
    "Документ подготовлен: 22 октября 2026 года.  ·  Объём проверки: 1 января — "
    "22 октября 2026 года.  ·  Формат: PDF, A4.", "Small"))


# ----------------------------------------------------------------------------- TOC notification
HEADINGS = []


def after_flowable(flowable):
    if isinstance(flowable, Paragraph):
        name = flowable.style.name
        if name == "H1":
            doc.notify("TOCEntry", (0, flowable.getPlainText(), doc.page))
            HEADINGS.append((0, flowable.getPlainText(), doc.page))
        elif name == "H2":
            doc.notify("TOCEntry", (1, flowable.getPlainText(), doc.page))
            HEADINGS.append((1, flowable.getPlainText(), doc.page))


doc.afterFlowable = after_flowable
doc.multiBuild(story, canvasmaker=NumberedCanvas)


# ----------------------------------------------------------------------------- bookmarks
def add_bookmarks(path, headings):
    """Добавляет закладки PDF по заголовкам (через PyMuPDF)."""
    try:
        import pymupdf
    except ImportError:  # pragma: no cover
        return
    pdf = pymupdf.open(path)
    toc = []
    seen = set()
    # содержание занимает стр. 3; поиск заголовков начинаем со стр. 4 (индекс 3)
    search_from = 3
    for level, title, page in headings:
        if title in seen:
            continue
        seen.add(title)
        needle = title[:44]
        found = None
        for pno in range(search_from, pdf.page_count):
            if pdf[pno].search_for(needle):
                found = pno + 1
                break
        if found is None:
            found = page
        toc.append([level + 1, title, found])
        search_from = max(3, found - 1)
    pdf.set_toc(toc)
    pdf.saveIncr()
    pdf.close()


add_bookmarks(OUT, HEADINGS)
print("PDF written:", OUT, "| headings:", len(HEADINGS))

try:
    import pymupdf
    _doc = pymupdf.open(OUT)
    print("Pages:", _doc.page_count,
          "| bookmarks:", len(_doc.get_toc()),
          "| size:", os.path.getsize(OUT), "bytes")
    _doc.close()
except ImportError:  # pragma: no cover
    pass
