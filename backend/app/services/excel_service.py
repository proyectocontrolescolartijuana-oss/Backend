from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


INVALID_SHEET_CHARS = set('[]:*?/\\')


def _column_letter(index: int) -> str:
    letters = ""

    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters

    return letters


def _clean_text(value) -> str:
    text = str(value)

    return "".join(
        char
        for char in text
        if char in "\t\n\r" or ord(char) >= 32
    )


def _escape(value) -> str:
    return (
        _clean_text(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _sheet_name(name: str, index: int, used_names: set[str]) -> str:
    cleaned = "".join(
        "_" if char in INVALID_SHEET_CHARS else char
        for char in _clean_text(name or f"Hoja {index}")
    ).strip("' ")

    cleaned = cleaned or f"Hoja {index}"
    base = cleaned[:31]
    candidate = base
    suffix = 2

    while candidate.lower() in used_names:
        ending = f" {suffix}"
        candidate = f"{base[:31 - len(ending)]}{ending}"
        suffix += 1

    used_names.add(candidate.lower())

    return candidate


def _format_value(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(value, date):
        return value.isoformat()

    return value


def _cell_xml(reference: str, value, style: int | None = None) -> str:
    value = _format_value(value)
    style_attr = f' s="{style}"' if style is not None else ""

    if value is None:
        return f'<c r="{reference}"{style_attr}/>'

    if isinstance(value, bool):
        return (
            f'<c r="{reference}" t="b"{style_attr}>'
            f"<v>{1 if value else 0}</v></c>"
        )

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{reference}"{style_attr}><v>{value}</v></c>'

    return (
        f'<c r="{reference}" t="inlineStr"{style_attr}>'
        f"<is><t>{_escape(value)}</t></is></c>"
    )


def _column_widths(headers: list[str], rows: list[dict]) -> str:
    columns = []

    for index, header in enumerate(headers, start=1):
        max_length = len(str(header))

        for row in rows:
            value = _format_value(row.get(header))

            if value is not None:
                max_length = max(max_length, len(str(value)))

        width = min(max(max_length + 2, 12), 45)
        columns.append(
            f'<col min="{index}" max="{index}" width="{width}" customWidth="1"/>'
        )

    return "<cols>" + "".join(columns) + "</cols>" if columns else ""


def _worksheet_xml(columns: list[dict], rows: list[dict]) -> str:
    headers = [column["header"] for column in columns]
    normalized_rows = [
        {
            column["header"]: row.get(column["key"])
            for column in columns
        }
        for row in rows
    ]
    max_column = _column_letter(max(len(headers), 1))
    last_row = max(len(normalized_rows) + 1, 1)
    dimension = f"A1:{max_column}{last_row}"

    xml_rows = []
    header_cells = [
        _cell_xml(
            f"{_column_letter(index)}1",
            header,
            style=1
        )
        for index, header in enumerate(headers, start=1)
    ]
    xml_rows.append(f'<row r="1">{"".join(header_cells)}</row>')

    for row_index, row in enumerate(normalized_rows, start=2):
        cells = [
            _cell_xml(
                f"{_column_letter(column_index)}{row_index}",
                row.get(header)
            )
            for column_index, header in enumerate(headers, start=1)
        ]
        xml_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    auto_filter = (
        f'<autoFilter ref="A1:{max_column}{last_row}"/>'
        if headers else ""
    )

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <dimension ref="{dimension}"/>
  <sheetViews>
    <sheetView workbookViewId="0">
      <pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>
    </sheetView>
  </sheetViews>
  {_column_widths(headers, normalized_rows)}
  <sheetData>
    {"".join(xml_rows)}
  </sheetData>
  {auto_filter}
</worksheet>'''


def _content_types_xml(sheet_count: int) -> str:
    sheets = "".join(
        (
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>'
        )
        for index in range(1, sheet_count + 1)
    )

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {sheets}
</Types>'''


def _root_rels_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''


def _workbook_xml(sheet_names: list[str]) -> str:
    sheets = "".join(
        (
            f'<sheet name="{_escape(name)}" sheetId="{index}" '
            f'r:id="rId{index}"/>'
        )
        for index, name in enumerate(sheet_names, start=1)
    )

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>{sheets}</sheets>
</workbook>'''


def _workbook_rels_xml(sheet_count: int) -> str:
    sheet_relationships = "".join(
        (
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/'
            f'relationships/worksheet" Target="worksheets/sheet{index}.xml"/>'
        )
        for index in range(1, sheet_count + 1)
    )
    styles_id = sheet_count + 1

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {sheet_relationships}
  <Relationship Id="rId{styles_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''


def _styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2">
    <font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/><family val="2"/></font>
  </fonts>
  <fills count="3">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF0B245B"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''


def _core_props_xml(title: str) -> str:
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:dcmitype="http://purl.org/dc/dcmitype/"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{_escape(title)}</dc:title>
  <dc:creator>Unifront</dc:creator>
  <cp:lastModifiedBy>Unifront</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>
</cp:coreProperties>'''


def _app_props_xml(sheet_names: list[str]) -> str:
    sheet_items = "".join(
        f'<vt:lpstr>{_escape(name)}</vt:lpstr>'
        for name in sheet_names
    )

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
  xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Unifront</Application>
  <HeadingPairs>
    <vt:vector size="2" baseType="variant">
      <vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant>
      <vt:variant><vt:i4>{len(sheet_names)}</vt:i4></vt:variant>
    </vt:vector>
  </HeadingPairs>
  <TitlesOfParts>
    <vt:vector size="{len(sheet_names)}" baseType="lpstr">{sheet_items}</vt:vector>
  </TitlesOfParts>
</Properties>'''


def build_xlsx(
    sheets: list[dict],
    *,
    title: str = "Reporte"
) -> bytes:
    output = BytesIO()
    used_names: set[str] = set()
    prepared_sheets = [
        {
            **sheet,
            "name": _sheet_name(sheet.get("name"), index, used_names)
        }
        for index, sheet in enumerate(sheets, start=1)
    ]
    sheet_names = [sheet["name"] for sheet in prepared_sheets]

    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml(len(sheets)))
        archive.writestr("_rels/.rels", _root_rels_xml())
        archive.writestr("xl/workbook.xml", _workbook_xml(sheet_names))
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            _workbook_rels_xml(len(sheets))
        )
        archive.writestr("xl/styles.xml", _styles_xml())
        archive.writestr("docProps/core.xml", _core_props_xml(title))
        archive.writestr("docProps/app.xml", _app_props_xml(sheet_names))

        for index, sheet in enumerate(prepared_sheets, start=1):
            archive.writestr(
                f"xl/worksheets/sheet{index}.xml",
                _worksheet_xml(sheet.get("columns", []), sheet.get("rows", []))
            )

    return output.getvalue()
