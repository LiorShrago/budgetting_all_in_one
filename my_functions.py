import csv
import numpy as np
from pprint import pprint
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext,simpledialog, messagebox, ttk
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView, QDialog, QHBoxLayout, QAbstractItemView
)
from PyQt5.QtCore import Qt

# def lists_from_dict (list_dictionnary_purchases):

def extract_fields_from_purchases(purchases_by_category):
    # Flatten all purchase dictionaries into a single list
    all_purchases = []
    for purchase_list in purchases_by_category.values():
        all_purchases.extend(purchase_list)
    
    # Find all unique keys across all purchases
    all_keys = set()
    for purchase in all_purchases:
        all_keys.update(purchase.keys())
    
    # Build a dictionary: key -> list of values for that key
    result = {key: [] for key in all_keys}
    for purchase in all_purchases:
        for key in all_keys:
            # Use None if the key is missing in a particular purchase
            result[key].append(purchase.get(key))
    
    return result

class CategoryDetailsDialog(QDialog):
    def __init__(self, category, sorted_purchases, sub_debit_sums, sub_credit_sums, sub_counts, grand_total, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Details for {category}")
        self.setMinimumSize(800, 400)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header
        net_debits = sum(p.get('debit', 0) for p in sorted_purchases[category])
        pct_of_total = (net_debits / grand_total * 100) if grand_total else 0
        layout.addWidget(QLabel(f"<b>{category} Statement</b>"))
        layout.addWidget(QLabel(f"Total: ${net_debits:,.2f} ({pct_of_total:.2f}% of Grand Total)"))

        # Table
        keywords = sub_counts[category]
        table = QTableWidget(len(keywords), 7)
        table.setHorizontalHeaderLabels([
            "Keyword", "Money Out", "Money In", "Count", "% of Cat.", "% of Total", "Details"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for row, kw in enumerate(sorted(keywords, key=lambda k: -sub_debit_sums[category][k])):
            kw_debit_sum = sub_debit_sums[category][kw]
            kw_credit_sum = sub_credit_sums[category][kw]
            kw_count = sub_counts[category][kw]
            if str(kw).upper() != 'MORTGAGE' and str(kw).upper() != 'TRANSFERS IN/OUT':
                pct_cat = (kw_debit_sum / net_debits * 100) if net_debits else 0
                pct_total = (kw_debit_sum / grand_total * 100) if grand_total else 0
            table.setItem(row, 0, QTableWidgetItem(kw))
            table.setItem(row, 1, QTableWidgetItem(f"${kw_debit_sum:,.2f}"))
            table.setItem(row, 2, QTableWidgetItem(f"${kw_credit_sum:,.2f}"))
            table.setItem(row, 3, QTableWidgetItem(str(kw_count)))
            table.setItem(row, 4, QTableWidgetItem(f"{pct_cat:.2f}%"))
            table.setItem(row, 5, QTableWidgetItem(f"{pct_total:.2f}%"))

            # Details Button
            btn = QPushButton("Show")
            btn.clicked.connect(lambda _, k=kw: self.show_keyword_transactions(category, k, sorted_purchases[category]))
            table.setCellWidget(row, 6, btn)

        layout.addWidget(table)

        # Close Button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def show_keyword_transactions(self, category, keyword, transactions):
        # Filter transactions for this keyword (sub-category)
        keyword_transactions = [p for p in transactions if keyword in p['description']]
        dialog = KeywordTransactionsDialog(category, keyword, keyword_transactions, self)
        dialog.exec_()

class KeywordTransactionsDialog(QDialog):
    def __init__(self, category, keyword, transactions, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{category} - {keyword} Transactions")
        self.setMinimumSize(900, 400)
        layout = QVBoxLayout()
        self.setLayout(layout)

        headers = ["Date", "Description", "Debit", "Credit", "Type"]
        table = QTableWidget(len(transactions), len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for row, purchase in enumerate(transactions):
            table.setItem(row, 0, QTableWidgetItem(str(purchase.get('date', ''))))
            table.setItem(row, 1, QTableWidgetItem(str(purchase.get('description', ''))))
            table.setItem(row, 2, QTableWidgetItem(str(purchase.get('debit', ''))))
            table.setItem(row, 3, QTableWidgetItem(str(purchase.get('credit', ''))))
            table.setItem(row, 4, QTableWidgetItem(str(purchase.get('type', ''))))

        layout.addWidget(table)

        # Close Button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

class MainWindow(QMainWindow):
    def __init__(self, categories, sorted_purchases, most_used, sub_debit_sums, sub_credit_sums, sub_counts, grand_total, returns, total_credit_pay, parsed_purchases, summary_text=''):
        super().__init__()
        self.setWindowTitle("Spending Categories")
        self.setMinimumSize(1000, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Header
        header = QLabel("<b>Spending Categories</b>")
        header.setStyleSheet("font-size: 22pt; color: #1a237e; margin-bottom: 12px;")
        layout.addWidget(header)

        # Table
        table = QTableWidget(len(categories), 5)
        headers = [
            "Category", "Total Debits (Money Out/Spent)", "Total Credits (Money In/Received)", "% of Total Debits", "Details"
        ]
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet("font-size: 11pt; background: #f8fafc;")
        for row, cat in enumerate(categories):
            net_credits = sum(p.get('credit', 0) for p in sorted_purchases[cat])
            net_debits = sum(p.get('debit', 0) for p in sorted_purchases[cat])
            pct_of_total = (net_debits / grand_total * 100) if grand_total else 0

            table.setItem(row, 0, QTableWidgetItem(str(cat)))
            table.setItem(row, 1, QTableWidgetItem(f"${net_debits:,.2f}"))
            table.setItem(row, 2, QTableWidgetItem(f"${net_credits:,.2f}"))
            if str(sorted_purchases.get('keyword', '')).upper() != 'MORTGAGE' and str(sorted_purchases.get('keyword', '')).upper() != 'TRANSFERS IN/OUT':
                table.setItem(row, 3, QTableWidgetItem(f"{pct_of_total:.2f}%"))
            btn = QPushButton("Details")
            btn.setStyleSheet("background: #1976d2; color: white; font-weight: bold;")
            btn.clicked.connect(
                lambda checked, c=cat: self.show_category_details_dialog(
                    c, sorted_purchases, sub_debit_sums, sub_credit_sums, sub_counts, grand_total
                )
            )
            table.setCellWidget(row, 4, btn)

        table.setAlternatingRowColors(True)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(table)

        # Footer
        from datetime import datetime
        if parsed_purchases:
            try:
                dates = [datetime.strptime(p['date'], "%Y-%m-%d") for p in parsed_purchases if 'date' in p]
                oldest_date = min(dates).strftime("%Y-%m-%d")
                newest_date = max(dates).strftime("%Y-%m-%d")
            except ValueError:
                oldest_date = "N/A"
                newest_date = "N/A"
        else: 
            oldest_date = "N/A"
            newest_date = "N/A"

        footer_text = (
            f"Start Date: {oldest_date}    End Date: {newest_date}\n\n"
            f"Total Money Spent - Credit Card Purchases: ${grand_total:,.2f}\n"
            f"Total Money Paid to Credit Cards: ${returns:,.2f}\n"
            f"Total Returns to Credit Cards: ${total_credit_pay:,.2f}\n"
            f"Total Cashflow In from bank accounts: ${total_credit_pay:,.2f}\n"
            f"Total Cashflow Out from bank accounts: ${total_credit_pay:,.2f}\n"
            f": ${total_credit_pay:,.2f}\n"

        )
        footer_label = QLabel(footer_text)
        footer_label.setStyleSheet("font-size: 12pt; color: #1a237e; font-weight: bold; margin-top: 18px;")
        layout.addWidget(footer_label, alignment=Qt.AlignLeft)

    def show_category_details_dialog(self, category, sorted_purchases, sub_debit_sums, sub_credit_sums, sub_counts, grand_total):
        dlg = CategoryDetailsDialog(category, sorted_purchases, sub_debit_sums, sub_credit_sums, sub_counts, grand_total, parent=self)
        dlg.exec_()

def show_main_window(categories, sorted_purchases, most_used, sub_debit_sums, sub_credit_sums, sub_counts, grand_total, returns, total_credit_pay, parsed_purchases, summary_text=''):
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(categories, sorted_purchases, most_used, sub_debit_sums, sub_credit_sums, sub_counts, grand_total, returns, total_credit_pay, parsed_purchases, summary_text)
    window.show()
    if not QApplication.instance():
        sys.exit(app.exec_())
    else:
        app.exec_()

def parse_multiple_csv(files_with_types):
    """
    files_with_types: list of tuples (filename, type_of_statement)
    Returns: combined list of all purchases from all files
    """
    all_transactions = []
    for filename, type_of_statement in files_with_types:
        purchases = parse_csv(filename, type_of_statement)
        all_transactions.extend(purchases)
    return all_transactions

def parse_csv(filename, type_of_statement):
    purchases,transactions = [],[]
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
                if (type_of_statement == 'cibc'):
                    date = row[0]
                    year, month, day = map(int,date.split('-'))
                    date_obj = datetime(year,month,day)
                    date = date_obj.strftime("%Y-%m-%d")
                    description = row[1]
                    try:
                        if row[2]:
                            debit = float(row[2])
                            purchases.append({'date': date, 'description': description, 'debit': debit, 'type': type_of_statement})
                        else:
                            credit = float(row[3])
                            purchases.append({'date': date, 'description': description, 'credit': credit, 'type': type_of_statement})
                    except ValueError:
                        print(f"Skipping invalid numeric value at row {i}: {row}")
                        continue
                elif (type_of_statement == 'simplii'):
                    date = row[0]
                    month, day, year = map(int,date.split('/'))
                    date_obj = datetime(year,month,day)
                    date = date_obj.strftime("%Y-%m-%d")
                    description = row[1]
                    try:
                        if row[2]:
                            debit = float(row[2]) 
                            purchases.append({'date': date, 'description': description, 'debit': debit, 'type': type_of_statement})
                        else:
                            credit = float(row[3])
                            purchases.append({'date': date, 'description': description, 'credit': credit, 'type': type_of_statement})
                    except ValueError:
                        print(f"Skipping invalid numeric value at row {i}: {row}")
                        continue
                    
                elif (type_of_statement == 'amex'):
                    date = row[0]
                    date = date.replace(".", "")
                    date_obj = datetime.strptime(str(date), "%d %b %Y")
                    date = date_obj.strftime("%Y-%m-%d")
                    description = row[1]
                    try:
                        debit = row[3] if row[3] else row[2]
                        debit = debit.replace("$","")
                        debit = debit.replace(",", "")
                        if '-' in debit: #the amount is a credit
                            credit= debit.replace("-","")
                            credit = float(credit)
                            purchases.append({'date': date, 'description': description, 'credit': credit, 'type': type_of_statement})
                        else:
                            debit = float(debit)
                            purchases.append({'date': date, 'description': description, 'debit': debit, 'type': type_of_statement})
                    except ValueError:
                        print(f"Skipping invalid numeric value at row {i}: {row}")
                        continue
                    
                elif (type_of_statement == 'eq'):
                    date = row[0]
                    date_obj = datetime.strptime(str(date), "%d-%b-%y")
                    date = date_obj.strftime("%Y-%m-%d")
                    description = row[1]
                    try:
                        debit = row[2]
                        debit = debit.replace("$","")
                        debit = debit.replace(",", "")
                        if '(' in debit: #the amount is in brackets () so it is a credit
                            credit = debit.replace("(","")
                            credit = credit.replace(")","")
                            credit = float(credit)
                            purchases.append({'date': date, 'description': description, 'credit': credit,'type': type_of_statement})
                        else:
                            debit = float(debit)
                            purchases.append({'date': date, 'description': description, 'debit': debit,'type': type_of_statement})
                    except ValueError:
                        print(f"Skipping invalid numeric value at row {i}: {row}")
                        continue
            else:
                print("Skipping invalid row at index", i, ":", row)
        #print(purchases)
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
            categorized_purchases['UNCATEGORIZED'].append(purchase)

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
    sub_category_debit_sums ,sub_category_credit_sums = {}, {}
    sub_category_counts = {}

    for category, purchases in sorted_purchases.items():
        keyword_counts = {kw: 0 for kw in categories.get(category, [])}
        keyword_debit_sums  = {kw: 0 for kw in categories.get(category, [])}
        keyword_credit_sums  = {kw: 0 for kw in categories.get(category, [])}

        for purchase in purchases:
            desc = purchase['description'].upper()
            for keyword in categories.get(category, []):
                if keyword in desc:
                    keyword_counts[keyword] += 1
                    keyword_debit_sums[keyword] += float(purchase.get('debit', 0)) 
                    keyword_credit_sums[keyword] += float(purchase.get('credit', 0))

        # Remove keywords that were never matched (count is zero)
        filtered_counts = {kw: cnt for kw, cnt in keyword_counts.items() if cnt > 0}
        filtered_debit_sums = {kw: keyword_debit_sums[kw] for kw in filtered_counts}
        filtered_credit_sums = {kw: keyword_credit_sums[kw] for kw in filtered_counts}
        if filtered_counts:
            # Find the keyword with the highest count
            most_common = max(filtered_counts.items(), key=lambda x: x[1])
            most_used_keywords[category] = most_common
        else:
            most_used_keywords[category] = (None, 0)  # No keyword found

        sub_category_debit_sums[category] = filtered_debit_sums        
        sub_category_credit_sums[category] = filtered_credit_sums

        sub_category_counts[category] = filtered_counts

    return most_used_keywords, sub_category_debit_sums,sub_category_credit_sums, sub_category_counts

