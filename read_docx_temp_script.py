import zipfile
import xml.etree.ElementTree as ET
import sys
import os
import codecs

def get_docx_text(path):
    if not os.path.exists(path):
        return f"File not found: {path}"
    
    try:
        document = zipfile.ZipFile(path)
        xml_content = document.read('word/document.xml')
        document.close()
        
        tree = ET.XML(xml_content)
        
        # Word processing namespace
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        paragraphs = []
        for paragraph in tree.findall('.//w:p', ns):
            text = []
            for run in paragraph.findall('.//w:r', ns):
                for text_node in run.findall('.//w:t', ns):
                    if text_node.text:
                        text.append(text_node.text)
            if text:
                paragraphs.append(''.join(text))
        return '\n'.join(paragraphs)
    except Exception as e:
        return f"Error reading docx: {str(e)}"

if __name__ == '__main__':
    if len(sys.argv) > 1:
        text = get_docx_text(sys.argv[1])
        with codecs.open('docx_output.txt', 'w', 'utf-8') as f:
            f.write(text)
    else:
        print("Please provide a path to a docx file")
