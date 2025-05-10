import csv
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext,simpledialog, messagebox, ttk


def show_category_details(category, sorted_purchases, sub_sums, sub_counts, grand_total):
    # Prepare data for the popup
    net_sum = sum(p['debit'] for p in sorted_purchases[category])
    keywords = {}
    for kw in sub_counts[category]:
        keywords[kw] = {
            'sum': sub_sums[category][kw],
            'count': sub_counts[category][kw]
        }

    detail_win = tk.Toplevel()
    detail_win.title(f"Details for {category}")
    detail_win.geometry('750x520')
    detail_win.configure(bg='#f4f6f8')

    # Frame with border and padding to mimic a statement panel
    frame = tk.Frame(detail_win, bg='white', bd=2, relief='groove', padx=18, pady=18)
    frame.pack(expand=True, fill='both', padx=25, pady=25)

    # Header label
    header = tk.Label(frame, text=f"{category.title()} Statement",
                      font=("Segoe UI", 18, "bold"), bg='white', fg='#1a237e')
    header.pack(anchor='w', pady=(0, 12))

    # Category total and percentage of grand total
    pct_of_total = (net_sum / grand_total * 100) if grand_total else 0
    summary = f"Total: ${net_sum:,.2f}   ({pct_of_total:.2f}% of Grand Total)\n"
    summary_label = tk.Label(frame, text=summary, font=("Segoe UI", 13, "bold"), bg='white', fg='#1565c0')
    summary_label.pack(anchor='w', pady=(0, 10))

    # Table header
    table_header = f"{'Keyword':<22} {'Sum':>13} {'Count':>7} {'% of Cat.':>13} {'% of Total':>13}\n"
    table_header += "-" * 75 + "\n"

    # Build the table rows
    table_rows = ""
    for kw, stats in sorted(keywords.items(), key=lambda x: -x[1]['sum']):
        kw_sum = stats['sum']
        kw_count = stats['count']
        pct_cat = (kw_sum / net_sum * 100) if net_sum else 0
        pct_total = (kw_sum / grand_total * 100) if grand_total else 0
        table_rows += f"{kw:<22} ${kw_sum:>12,.2f} {kw_count:>7} {pct_cat:>12.2f}% {pct_total:>12.2f}%\n"

    # Scrollable, monospace table
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 11), bg='#f8fafc', fg='#222222', bd=1, relief='solid', height=18)
    text_area.pack(expand=True, fill='both')
    text_area.insert(tk.END, table_header + table_rows)
    text_area.config(state='disabled')

    close_btn = tk.Button(frame, text="Close", command=detail_win.destroy, font=("Segoe UI", 11, "bold"), bg='#1976d2', fg='white', bd=0, relief='flat', padx=12, pady=6, activebackground='#1565c0')
    close_btn.pack(pady=12, anchor='e')

    detail_win.resizable(False, False)

def open_category_popup(category, sorted_purchases, sub_sums, sub_counts, grand_total):
    # Prepare details_dict for the popup
    net_sum = sum(p['debit'] for p in sorted_purchases[category])
    keywords = {}
    for kw in sub_counts[category]:
        keywords[kw] = {
            'sum': sub_sums[category][kw],
            'count': sub_counts[category][kw]
        }
    details_dict = {'net_sum': net_sum, 'keywords': keywords}
    show_category_details(category, details_dict, grand_total)


def show_main_window(categories, sorted_purchases, most_used, sub_sums, sub_counts, summary_text,
                     grand_total, returns, total_credit_pay, parsed_purchases):

    root = tk.Tk()
    root.title("Spending Categories")
    root.geometry('1500x900')
    root.configure(bg='#f4f6f8')

    # --- Create a main frame for the canvas and scrollbar ---
    main_frame = tk.Frame(root, bg='#f4f6f8')
    main_frame.pack(fill=tk.BOTH, expand=1)

    # --- Create a canvas ---
    canvas = tk.Canvas(main_frame, bg='#f4f6f8', highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # --- Add a vertical scrollbar to the canvas ---
    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # --- Configure the canvas to use the scrollbar ---
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # --- Create a frame inside the canvas ---
    inner_frame = tk.Frame(canvas, bg='#f4f6f8')
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # --- Optional: Enable mousewheel scrolling ---
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # --- Now add all your widgets to inner_frame instead of root/card ---
    # Main card/frame for content
    card = tk.Frame(inner_frame, bg='white', bd=2, relief='groove', padx=28, pady=28)
    card.pack(expand=True, fill='both', padx=40, pady=40)

    # Summary section (if present)
    if summary_text and str(summary_text).strip() != "0":
        summary_label = tk.Label(card, text="Summary", font=("Segoe UI", 16, "bold"), bg='white', fg='#1a237e')
        summary_label.pack(anchor='w', pady=(0, 8))
        summary_area = tk.Text(card, height=8, wrap=tk.WORD, font=("Segoe UI", 12), bg='#f9f9f9', fg='#222', bd=1, relief='solid')
        summary_area.pack(fill='x', padx=0)
        summary_area.insert(tk.END, summary_text)
        summary_area.config(state='disabled')
        sep = tk.Label(card, text="Categories", font=("Segoe UI", 15, "bold"), bg='white', fg='#1976d2')
        sep.pack(pady=(18, 8), anchor='w')
    else:
        sep = tk.Label(card, text="Categories", font=("Segoe UI", 15, "bold"), bg='white', fg='#1976d2')
        sep.pack(pady=(0, 8), anchor='w')

    # Table frame
    table = tk.Frame(card, bg='white')
    table.pack(fill='x', pady=10)

    # Table headers
    headers = [
        ("Category", 20),
        ("Net Sum", 16),
        ("Most Common Keyword", 25),
        ("Sum for Most Common Keyword", 28),
        ("", 2)
    ]
    for col, (text, width) in enumerate(headers):
        tk.Label(table, text=text, font=("Segoe UI", 12, "bold"), bg='white', fg='#374151',
                 anchor='w', width=width).grid(row=0, column=col, sticky='w', padx=(0, 4), pady=(0, 4))

    # Table rows
    for i, cat in enumerate(categories, start=1):
        net_sum = sum(purchase['debit'] for purchase in sorted_purchases[cat])
        most_common_keyword = most_used[cat][0] if most_used[cat][0] else "N/A"
        most_common_sum = sub_sums[cat].get(most_common_keyword, 0.0)
        pct_of_total = (net_sum / grand_total * 100) if grand_total else 0
        pct_of_cat = (most_common_sum / net_sum * 100) if net_sum else 0
        pct_of_total_kw = (most_common_sum / grand_total * 100) if grand_total else 0

        # Main row
        tk.Label(table, text=cat, bg='white', anchor='w', font=("Segoe UI", 11), width=20).grid(row=2*i-1, column=0, sticky='w')
        tk.Label(table, text=f"${net_sum:,.2f}", bg='white', anchor='w', font=("Segoe UI", 11), width=16).grid(row=2*i-1, column=1, sticky='w')
        tk.Label(table, text=most_common_keyword, bg='white', anchor='w', font=("Segoe UI", 11), width=25).grid(row=2*i-1, column=2, sticky='w')
        tk.Label(table, text=f"${most_common_sum:,.2f}", bg='white', anchor='w', font=("Segoe UI", 11), width=28).grid(row=2*i-1, column=3, sticky='w')

        # Styled Details button
        btn = tk.Button(table, text="Details", width=10,
                        font=("Segoe UI", 10, "bold"), bg='#1976d2', fg='white', bd=0, relief='flat',
                        activebackground='#1565c0', activeforeground='white',
                        cursor='hand2')
        btn.grid(row=2*i-1, column=4, padx=4, pady=2, sticky='w')
        btn.config(command=lambda c=cat: show_category_details(
            c, sorted_purchases, sub_sums, sub_counts, grand_total
        ))

        # Percentage row (smaller, gray font)
        tk.Label(table, text="", bg='white', width=20).grid(row=2*i, column=0)
        tk.Label(table, text=f"{pct_of_total:.2f}% of Total", font=("Segoe UI", 10), fg="#888", bg='white', anchor='w', width=16).grid(row=2*i, column=1, sticky='w')
        tk.Label(table, text="", bg='white', width=25).grid(row=2*i, column=2)
        tk.Label(table,
                 text=f"{pct_of_cat:.2f}% of Cat., {pct_of_total_kw:.2f}% of Total",
                 font=("Segoe UI", 10), fg="#888", bg='white', anchor='w', width=28).grid(row=2*i, column=3, sticky='w')
        tk.Label(table, text="", bg='white', width=2).grid(row=2*i, column=4)

    # --- Footer with grand totals and date range ---
    if parsed_purchases:
        try:
            dates = [datetime.strptime(p['date'], "%Y-%m-%d") for p in parsed_purchases if 'date' in p]
            oldest_date = min(dates).strftime("%Y-%m-%d")
            newest_date = max(dates).strftime("%Y-%m-%d")
        except Exception:
            oldest_date = "N/A"
            newest_date = "N/A"
    else:
        oldest_date = "N/A"
        newest_date = "N/A"

    footer_text = (
        f"Start Date: {oldest_date}    End Date: {newest_date}\n\n"
        f"Grand Total Spent: ${grand_total:,.2f}\n"
        f"Total Returns: ${returns:,.2f}\n"
        f"Total Credit Payment: ${total_credit_pay:,.2f}\n"
    )

    footer_label = tk.Label(card, text=footer_text, font=("Segoe UI", 12, "bold"),
                            bg='white', fg='#1a237e', anchor='w', justify='left')
    footer_label.pack(side='top', fill='x', padx=0, pady=18)

    root.mainloop()

# --- Build the summary string with per-category totals ---

def build_summary_string(categories, sorted_purchases, parsed_purchases, grand_total, returns, total_credit_pay):
    summary_lines = []
    summary_lines.append(f"{len(sorted_purchases['uncategorized'])} out of {len(parsed_purchases)} Uncategorized purchases\n")
    summary_lines.append(f"{'Category':>25} - {'Total Spent':<12} {'Credit':<12}")

    # Per-category totals
    for category in categories:
        total_spent = 0
        credit_payment = 0
        for purchase in sorted_purchases[category]:
            if purchase['debit'] < 0:
                credit_payment += purchase['debit']
            else:
                total_spent += purchase['debit']
        summary_lines.append(f"{category:>25} - ${total_spent:<10.2f} ${credit_payment:<10.2f}")

    summary_lines.append(f"\n==> Grand Total Spent: ${grand_total:<10.2f} Total Returns: ${returns:<10.2f} Total Credit Payment: ${total_credit_pay:<10.2f}\n")
    return "\n".join(summary_lines)

def parse_csv(filename, type_of_satement):
    purchases = []
    with open(filename, 'r', newline='') as file:
        sample = file.read(2048)  # Read a sample of the file (2 KB is usually enough)
        file.seek(0)  # Go back to the start of the file after reading the sample

        has_header = csv.Sniffer().has_header(sample)
        if has_header:
            print("Header detected in the first row.")
            next(file)  # Skip the header line
        else:
            print("No header detected in the first row.")

        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if len(row) >= 4:
                if (type_of_satement == 'mastercard'):
                    date = row[0]
                    description = row[1]
                    try:
                        debit = float(row[2]) if row[2] else -float(row[3])
                    except ValueError:
                        print(f"Skipping invalid numeric value at row {i}: {row}")
                        continue
                    purchases.append({'date': date, 'description': description, 'debit': debit})
            else:
                print("Skipping invalid row at index", i, ":", row)
    return purchases

def categorize_purchases(purchases, categories):
    # Ensure all keywords in categories are uppercase
    categories = {category: [keyword.upper() for keyword in keywords] for category, keywords in categories.items()}
    
    # Initialize dictionary for categories
    categorized_purchases = {category: [] for category in categories}

    for purchase in purchases:
        description = purchase['description'].upper()  # Convert description to uppercase for case-insensitive matching
        categorized = False

        # Check if any keyword matches the description
        for category, keywords in categories.items():
            if any(keyword in description for keyword in keywords):
                categorized_purchases[category].append(purchase)
                categorized = True
                break  # Stop checking other categories once a match is found

        # If no category matches, add to 'uncategorized'
        if not categorized:
            categorized_purchases['uncategorized'].append(purchase)

    return categorized_purchases

def review_uncategorized_purchases(categorized_purchases, purchases, categories):
    """
    Allows the user to review and categorize uncategorized purchases using a pop-up dialog.
    Modifies categorized_purchases and categories in-place.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    def get_uncategorized():
        return categorized_purchases.get('uncategorized', [])

    while get_uncategorized():
        uncategorized = get_uncategorized()
        purchase = uncategorized[0]  # Always handle the first uncategorized purchase

        # Prepare the message
        msg = f"Date: {purchase['date']}\nDescription: {purchase['description']}\nAmount: {purchase['debit']}\n\n"
        msg += "Choose a category or create a new one:"

        # List of categories (excluding 'uncategorized')
        category_list = [cat for cat in categories if cat != 'uncategorized']

        # Pop-up dialog for category selection
        category = simpledialog.askstring(
            "Categorize Purchase",
            f"{msg}\n\nExisting categories: {', '.join(category_list)}\n\nType a category name or NEW:<name> to create one."
        )

        if category is None:
            # User cancelled; ask if they want to stop
            if messagebox.askyesno("Exit?", "Do you want to stop categorizing?"):
                break
            else:
                continue

        category = category.strip()
        if category.lower().startswith('new:'):
            # Create a new category
            new_category = category[4:].strip()
            if new_category:
                if new_category not in categories:
                    categories[new_category] = []
                # Ask for a keyword for this category
                keyword = simpledialog.askstring("New Category", f"Enter a keyword for category '{new_category}':")
                if keyword:
                    categories[new_category].append(keyword.upper())
                else:
                    messagebox.showwarning("No keyword", "No keyword entered. Category not created.")
                    continue
            else:
                messagebox.showwarning("Invalid", "No category name entered.")
                continue
        elif category not in categories:
            # Add to existing categories if not present
            categories[category] = []

        # Assign the purchase to the chosen category
        # Add a keyword for future auto-categorization if needed
        if category not in categories:
            categories[category] = []
        # Optionally: ask for a new keyword for this category
        if not any(keyword in purchase['description'].upper() for keyword in categories[category]):
            add_keyword = messagebox.askyesno("Add Keyword?", f"Do you want to add a keyword from this description to category '{category}' for future auto-categorization?")
            if add_keyword:
                keyword = simpledialog.askstring("Add Keyword", "Enter a keyword to match for this category:")
                if keyword:
                    categories[category].append(keyword.upper())

        # Remove from uncategorized and add to the chosen category
        categorized_purchases['uncategorized'].remove(purchase)
        if category not in categorized_purchases:
            categorized_purchases[category] = []
        categorized_purchases[category].append(purchase)

        # Optionally, re-categorize all purchases using the updated categories
        # This ensures similar purchases are auto-categorized in the next loop
        categorized_purchases = categorize_purchases(purchases, categories)

    root.destroy()
    return categorized_purchases, categories

def analyze_category_keywords(sorted_purchases, categories):
    # Ensure all keywords in categories are uppercase (for matching)
    categories = {cat: [kw.upper() for kw in kws] for cat, kws in categories.items()}
    most_used_keywords = {}
    sub_category_sums = {}
    sub_category_counts = {}

    for category, purchases in sorted_purchases.items():
        keyword_counts = {kw: 0 for kw in categories.get(category, [])}
        keyword_sums = {kw: 0 for kw in categories.get(category, [])}

        for purchase in purchases:
            desc = purchase['description'].upper()
            for keyword in categories.get(category, []):
                if keyword in desc:
                    keyword_counts[keyword] += 1
                    keyword_sums[keyword] += purchase.get('debit', 0)

        # Remove keywords that were never matched (count is zero)
        filtered_counts = {kw: cnt for kw, cnt in keyword_counts.items() if cnt > 0}
        filtered_sums = {kw: keyword_sums[kw] for kw in filtered_counts}

        if filtered_counts:
            # Find the keyword with the highest count
            most_common = max(filtered_counts.items(), key=lambda x: x[1])
            most_used_keywords[category] = most_common
        else:
            most_used_keywords[category] = (None, 0)  # No keyword found

        sub_category_sums[category] = filtered_sums
        sub_category_counts[category] = filtered_counts

    return most_used_keywords, sub_category_sums, sub_category_counts