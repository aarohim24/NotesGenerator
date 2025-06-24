class NotesExporter:
    
    @staticmethod
    def to_markdown(notes):
        return f"# Study Notes\n\n{notes.replace('\n', '\n\n')}"
    
    @staticmethod
    def to_html(notes):
        return f"""<html><body><h1>Study Notes</h1><pre>{notes}</pre></body></html>"""
