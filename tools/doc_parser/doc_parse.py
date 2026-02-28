from docx import Document


def parse_docx(filepath):
    doc = Document(filepath)

    print(doc.tables)


if __name__ == "__main__":
    parse_docx(
        "C:/Users/Austin Conner/Documents/HackUSU/Debbie/Debbie/tools/doc_parser/jsa_blank.docx")
