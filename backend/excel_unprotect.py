import tempfile
import os
import shutil
import zipfile
from lxml import etree

NS = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def remove_protection(file_bytes: bytes, filename: str) -> tuple[bytes, str]:
    """
    接收 Excel 檔案 bytes，移除 sheet/workbook 保護後，回傳新的檔案 bytes 與檔名
    （不會永久儲存檔案）
    """

    tmpdir = tempfile.mkdtemp()

    # 寫入原始檔案
    input_path = os.path.join(tmpdir, filename)
    with open(input_path, "wb") as f:
        f.write(file_bytes)

    # 解壓縮 Excel (ZIP)
    with zipfile.ZipFile(input_path, "r") as z:
        z.extractall(tmpdir)

    changed = False

    # 處理工作表 XML
    ws_dir = os.path.join(tmpdir, "xl", "worksheets")
    if os.path.exists(ws_dir):
        for f in os.listdir(ws_dir):
            if f.endswith(".xml"):
                if _clean_xml(os.path.join(ws_dir, f)):
                    changed = True

    # 處理活頁簿 XML
    wb_xml = os.path.join(tmpdir, "xl", "workbook.xml")
    if os.path.exists(wb_xml):
        if _clean_xml(wb_xml):
            changed = True

    # 如果沒有變化 → 回傳原檔案
    if not changed:
        output_bytes = open(input_path, "rb").read()
        shutil.rmtree(tmpdir)
        return output_bytes, filename

    # 重新壓縮新的 Excel
    new_filename = _generate_output_name(filename)
    output_path = os.path.join(tmpdir, new_filename)

    # 重新壓縮成新檔案（保留 ZIP 結構）
    new_filename = _generate_output_name(filename)
    output_path = os.path.join(tmpdir, new_filename)

    # 🚫 不能用 os.walk() 直接壓縮整個資料夾，
    # 🔥 需讀原 ZIP 順序逐檔寫入，避免 Excel 結構異常。
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as new_zip:
        with zipfile.ZipFile(input_path, "r") as old_zip:
            for item in old_zip.infolist():
                # 取得原始檔案
                extracted_path = os.path.join(tmpdir, item.filename)

                # 如果是我們改過的 XML，寫入修改後的內容
                if os.path.exists(extracted_path):
                    with open(extracted_path, "rb") as f:
                        new_zip.writestr(item, f.read())
                else:
                    # 不在解壓目錄，就直接寫回（保持一致性）
                    data = old_zip.read(item.filename)
                    new_zip.writestr(item, data)


    # 回傳 bytes
    output_bytes = open(output_path, "rb").read()
    shutil.rmtree(tmpdir)
    return output_bytes, new_filename


# ---------------------------------------------------------
# 內部輔助函式
# ---------------------------------------------------------

def _clean_xml(xml_path: str) -> bool:
    """刪除 XML 中的 sheetProtection 和 workbookProtection，回傳是否更動"""
    if not os.path.exists(xml_path):
        return False

    before = open(xml_path, "rb").read()

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml_path, parser)
    root = tree.getroot()

    removed = False
    for tag in ["sheetProtection", "workbookProtection"]:
        for elem in root.xpath(f"//ns:{tag}", namespaces=NS):
            elem.getparent().remove(elem)
            removed = True

    if removed:
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)

    after = open(xml_path, "rb").read()
    return before != after


def _generate_output_name(filename: str) -> str:
    """將 example.xlsx 轉 example_unprotected.xlsx"""
    name, ext = os.path.splitext(filename)
    return f"{name}_unprotected{ext}"