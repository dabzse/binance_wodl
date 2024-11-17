import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re


words = []
filtered_words = []
selected_word = None
file_name = "wodl.txt"


def load_words_from_file(default=False):
    global words
    if default and os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            words = clean_words(file.read())
            update_word_list(words)
            save_sorted_words(words)
    else:
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                words = clean_words(file.read())
                update_word_list(words)
                save_sorted_words(words)


def clean_words(text):
    word_list = re.findall(r"\b[A-Za-z]{3,}\b", text)
    cleaned_words = [word.upper() for word in word_list]
    cleaned_words = sorted(set(cleaned_words))
    return cleaned_words


def save_sorted_words(words):
    if words:
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(" ".join(words))


def update_word_list(word_list):
    for widget in word_frame.winfo_children():
        widget.destroy()

    if not word_list:
        return

    max_words_per_row = 6 if all(len(word) < 6 for word in word_list) else 5
    cell_width = 120 if max_words_per_row == 5 else 80

    rows = [
        word_list[i : i + max_words_per_row]
        for i in range(0, len(word_list), max_words_per_row)
    ]
    for row in rows:
        row_frame = tk.Frame(word_frame)
        row_frame.pack(fill=tk.X)
        for word in row:
            btn = tk.Button(
                row_frame,
                text=word,
                command=lambda w=word: select_word(w),
                width=cell_width // 10,
            )
            btn.pack(side=tk.LEFT, padx=4, pady=4)


def filter_words_by_length(event=None):
    global filtered_words
    try:
        length = length_entry.get()
        exclude_chars = exclude_entry.get().upper()
        if not length:
            filtered_words = [
                word
                for word in words
                if all(char not in word for char in exclude_chars)
            ]
        else:
            length = int(length)
            filtered_words = [
                word
                for word in words
                if len(word) == length
                and all(char not in word for char in exclude_chars)
            ]
            if not filtered_words:
                messagebox.showinfo("Info", "No matches found.")
                length_entry.focus_set()
            else:
                update_word_list(filtered_words)

        pattern_entry.focus_set()

    except ValueError:
        messagebox.showerror("Error", "Invalid length!")
        length_entry.focus_set()


def real_time_search(event=None):
    global filtered_words
    search_term = search_entry.get().upper()
    exclude_chars = exclude_entry.get().upper()

    if not length_entry.get():
        filtered_words = [
            word
            for word in words
            if word.startswith(search_term)
            and all(char not in word for char in exclude_chars)
        ]
    else:
        length = int(length_entry.get())
        filtered_words = [
            word
            for word in filtered_words
            if word.startswith(search_term)
            and len(word) == length
            and all(char not in word for char in exclude_chars)
        ]

    update_word_list(filtered_words)


def apply_pattern(event=None):
    global filtered_words, selected_word
    pattern = pattern_entry.get()

    if not selected_word:
        messagebox.showerror("Error", "Select a word first!")
        return

    if not valid_pattern(pattern):
        messagebox.showerror(
            "Error",
            "Invalid pattern. Only '+', '-', '.' characters are allowed.",
        )
        return

    filtered_words = [
        word for word in filtered_words if matches_pattern(word, selected_word, pattern)
    ]
    update_word_list(filtered_words)


def valid_pattern(pattern):
    if len(pattern) != len(selected_word):
        return False
    allowed_chars = set("+-.")
    return all(c in allowed_chars for c in pattern)


def matches_pattern(word, selected_word, pattern):
    if len(word) != len(selected_word):
        return False

    for i, char in enumerate(pattern):
        if char == "+":
            if word[i] != selected_word[i]:
                return False
        elif char == ".":
            if word[i] == selected_word[i] or selected_word[i] not in word:
                return False
        elif char == "-":
            if selected_word[i] in word:
                return False
    return True


def select_word(word):
    global selected_word, filtered_words
    selected_word = word
    selected_word_display.config(text=word)
    length_entry.delete(0, tk.END)
    length_entry.insert(0, str(len(word)))


def confirm_solution():
    root.quit()


def add_new_word(new_word):
    global words
    new_word_cleaned = new_word.strip().upper()
    if new_word_cleaned and new_word_cleaned not in words:
        words.append(new_word_cleaned)
        words = sorted(set(words))
        save_sorted_words(words)
        update_word_list(words)
        add_word_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "The new word is empty or already exists.")


def on_configure(event):
    word_canvas.configure(scrollregion=word_canvas.bbox("all"))


root = tk.Tk()
root.title("WODL finder")
root.minsize(815, 600)

scrollbar = tk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

word_canvas = tk.Canvas(root, yscrollcommand=scrollbar.set)
word_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=word_canvas.yview)

word_frame = tk.Frame(word_canvas)
word_canvas.create_window((0, 0), window=word_frame, anchor="nw")

word_frame.bind("<Configure>", on_configure)

loaded_label = tk.Label(root, text="Loaded file")
loaded_label.pack()
file_name_label = tk.Label(root, text=file_name, font=("Liberation Serif", 12, "bold"))
file_name_label.pack()

load_words_from_file(default=True)

file_button = tk.Button(
    root, text="Browse...", command=lambda: load_words_from_file(default=False)
)
file_button.pack()

search_label = tk.Label(root, text="Search:")
search_label.pack()

search_entry = tk.Entry(root)
search_entry.pack()
search_entry.bind("<KeyRelease>", real_time_search)

exclude_label = tk.Label(root, text="Exclude characters:")
exclude_label.pack()

exclude_entry = tk.Entry(root)
exclude_entry.pack()

length_label = tk.Label(root, text="Specify word length")
length_label.pack()

length_entry = tk.Entry(root)
length_entry.pack()
length_entry.bind("<Return>", filter_words_by_length)

filter_button = tk.Button(
    root, text="Filter by length", command=filter_words_by_length
)
filter_button.pack()

pattern_label = tk.Label(root, text="Specify pattern (+ - .)")
pattern_label.pack()

pattern_entry = tk.Entry(root)
pattern_entry.pack()
pattern_entry.bind("<Return>", apply_pattern)

selected_word_text = tk.Label(
    root, text="Chosen word", font=("Liberation Sans", 12, "bold")
)
selected_word_text.pack()

selected_word_display = tk.Label(root, text="", font=("Liberation Sans", 12, "bold"))
selected_word_display.pack()

confirm_button = tk.Button(root, text="Solution", command=confirm_solution)
confirm_button.pack()

add_word_label = tk.Label(root, text="Add new word:")
add_word_label.pack(pady=(10, 0))

add_word_entry = tk.Entry(root)
add_word_entry.pack()

add_word_button = tk.Button(
    root, text="Add", command=lambda: add_new_word(add_word_entry.get())
)
add_word_button.pack(pady=(5, 10))

root.mainloop()
