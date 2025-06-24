import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from document_processor import DocumentProcessor
from ai_generator import AINotesGenerator
from exporter import NotesExporter

class NotesGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Notes Generator")
        self.root.geometry("800x600")
        
        self.processor = DocumentProcessor()
        self.generator = AINotesGenerator()
        self.exporter = NotesExporter()
        
        self.setup_ui()
        self.setup_menu()
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.browse_input)
        file_menu.add_command(label="Save As", command=self.browse_output)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        export_menu = tk.Menu(menubar, tearoff=0)
        export_menu.add_command(label="Anki Deck", command=lambda: self.export("anki"))
        export_menu.add_command(label="Markdown", command=lambda: self.export("markdown"))
        export_menu.add_command(label="HTML", command=lambda: self.export("html"))
        menubar.add_cascade(label="Export", menu=export_menu)
        
        self.root.config(menu=menubar)
    
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        
        self.gen_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.gen_tab, text='Generate')
        
        tk.Label(self.gen_tab, text="Input File:").pack(pady=5)
        self.input_frame = ttk.Frame(self.gen_tab)
        self.input_frame.pack()
        self.input_entry = ttk.Entry(self.input_frame, width=50)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.input_frame, text="Browse", command=self.browse_input).pack(side=tk.LEFT)
        
        tk.Label(self.gen_tab, text="Output File:").pack(pady=5)
        self.output_frame = ttk.Frame(self.gen_tab)
        self.output_frame.pack()
        self.output_entry = ttk.Entry(self.output_frame, width=50)
        self.output_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.output_frame, text="Browse", command=self.browse_output).pack(side=tk.LEFT)
        
        tk.Label(self.gen_tab, text="Note Style:").pack(pady=5)
        self.style_var = tk.StringVar()
        self.style_menu = ttk.Combobox(self.gen_tab, textvariable=self.style_var,
                                    values=["Bullet Points", "Outline", "Summary", "Q&A Flashcards"])
        self.style_menu.pack()
        self.style_menu.set("Bullet Points")
        
        tk.Label(self.gen_tab, text="Detail Level:").pack(pady=5)
        self.detail_slider = ttk.Scale(self.gen_tab, from_=1, to=5, orient=tk.HORIZONTAL)
        self.detail_slider.pack()
        
        tk.Label(self.gen_tab, text="Custom Prompt:").pack(pady=5)
        self.prompt_text = tk.Text(self.gen_tab, height=5, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.X, padx=10)
        self.prompt_text.insert(tk.END, "Generate study notes with key concepts...")
        
        self.progress_frame = ttk.Frame(self.gen_tab)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Ready")
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        
        self.time_label = ttk.Label(self.progress_frame, text="Estimated time: --")
        self.time_label.pack()
        
        self.btn_frame = ttk.Frame(self.gen_tab)
        self.btn_frame.pack(pady=10)
        
        ttk.Button(self.btn_frame, text="Generate", command=self.start_generation).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Stop", command=self.stop_generation).pack(side=tk.LEFT, padx=5)
        
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text='Results')
        
        self.results_text = tk.Text(self.results_tab, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
    
    def browse_input(self):
        filetypes = [("Documents", "*.pdf *.docx")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)
    
    def browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("Markdown", "*.md")]
        )
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)
    
    def start_generation(self):
        input_path = self.input_entry.get()
        output_path = self.output_entry.get()
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        
        if not input_path or not output_path:
            messagebox.showerror("Error", "Please specify files")
            return
        
        try:
            open(output_path, 'w').close()
            text = self.processor.extract_text(input_path)
            
            thread = threading.Thread(
                target=self._generate_thread,
                args=(text, output_path, prompt),
                daemon=True
            )
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def _generate_thread(self, text, output_path, prompt):
        start_time = time.time()
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = 100
        
        try:
            if "Flashcards" in self.style_var.get():
                result = self.generator.generate_flashcards(text)
                notes = "\n".join([f"Q: {q}\nA: {a}\n" for q, a in result])
                open(output_path, 'w').write(notes)
            else:
                notes = self.generator.generate_notes(text, prompt)
                open(output_path, 'w', encoding='utf-8').write(notes)
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, notes)
            self.notebook.select(self.results_tab)
            
            elapsed = time.time() - start_time
            self.progress_label.config(text=f"Done in {elapsed:.1f}s")
            self.progress_bar['value'] = 100
            
        except Exception as e:
            self.progress_label.config(text=f"Error: {str(e)}")
    
    def stop_generation(self):
        self.generator.stop_generation = True
        self.progress_label.config(text="Stopping...")
    
    def export(self, format):
        notes = self.results_text.get(1.0, tk.END)
        if not notes.strip():
            messagebox.showerror("Error", "No notes to export")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[(format.upper(), f"*.{format}")]
        )
        if not path:
            return
        
        try:
            if format == "anki":
                content = self.exporter.to_anki(self._parse_flashcards(notes))
            elif format == "markdown":
                content = self.exporter.to_markdown(notes)
            elif format == "html":
                content = self.exporter.to_html(notes)
            else:
                raise ValueError("Unsupported format")
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("Success", f"Saved to {path}")
            
        except Exception as e:
            messagebox.showerror("Failed", str(e))
    
    def _parse_flashcards(self, text):
        cards = []
        current_q = None
        
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('Q:'):
                if current_q:
                    cards.append((current_q, ""))
                current_q = line[2:].strip()
            elif line.startswith('A:') and current_q:
                cards.append((current_q, line[2:].strip()))
                current_q = None
        
        if current_q:
            cards.append((current_q, ""))
        return cards
