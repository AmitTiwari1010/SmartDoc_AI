import zipfile
import xml.etree.ElementTree as ET
import sys

def read_docx(path):
    try:
        with zipfile.ZipFile(path) as docx:
            tree = ET.XML(docx.read('word/document.xml'))
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            return '\n'.join([node.text for node in tree.findall('.//w:t', namespaces) if node.text])
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    content = read_docx(r'c:\Users\amit7\Desktop\SmartDoc_AI\SmartDocs_AI_Document_Intelligence_RAG_MCP_Logic.docx')
    print(content)
