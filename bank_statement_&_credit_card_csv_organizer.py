# import csv
# import numpy as np
# from datetime import datetime
# import tkinter as tk
# from tkinter import scrolledtext,simpledialog, messagebox, ttk
import my_functions

rows,row, columns,col = [],[],[],[]
parsed_purchases, sorted_purchases = [], []
i,c,j=0,0,0
result_string = ""
categories= {'grocery':            ['COSTCO','DOLLAR','NOFRILLS','FARM BOY','FOOD BASICS', 'WAL-MART', 'SUPERSTORE', 'LONGOS','LOBLAWS','METRO','FRESHCO','FOODLAND','GROCERY','GOODMAN','T&T',
                                    'RANCHFRESH','VINCE'] 
            ,'restaurant':         ['CHATIME','POKE BOX' ,'NOODLE LEGEND', 'POS MERCHANDISE','SOUPS', 'ONROUTE','MABU' , 'CARIBB', 'AMD THORNHILL', 'MOXIES','MEVAME', 'WHAT A BAGEL','DELIVERO',
                                    'PATTIES', 'MARIACHI','BREWING', 'A&W', 'SEAFOOD','COBS','SALT','LOBSTER','ISAAN DER' , 'GOLS','SHAWARMA', 'KIMPTON','HUNGRY' , 'TIM HORTON','MCDONALD',
                                    'TACO','KFC','GELATO','EATS','PIZZA','BURGER','WINGS','RESTAURANT','CAFE','COFFEE','DINNER','LUNCH','BREAKFAST','BAGEL','SANDWICH','SUSHI','TACOS',
                                    'BUBBLE TEA','BOBA','TEA','FOOD TRUCK','FOOD COURT','FOOD HALL','FAST FOOD', 'GYUBEE', 'JAPANE', 'DUMPLING','KING SLICE','COCOA40','SUNSHINE VILLAGE GRILL',
                                    'SHENGJIAN KING',"SHELBY'S",'KIBO' ,'CHICKEN','BAR AND GRIL','EARLS'] 
            ,'gas':                ['SHELL','PETRO CANADA','ESSO','ULTRAMAR','PIONEER','GAS','FUEL','PETRO']
            ,'shopping':           ['FADES','BBYMARKETPLACE', 'STOKES','MACS', 'STORE ', 'VARIET','NUT SHOPP', 'SEPHORA','SHOPPER','AMZN','VALUE VILLAGE','TEMU','INDIGO','THRIFT','MARKET BRIGHTON',
                                    'CHAPTERS' ,'EBAY','STINSON & SON','WALMART','BEST BUY','MARSHALLS','HOME DEPOT','LOWES','CANADIAN TIRE', 'STAPLES','TREASURE HUNT','PARTY CITY','ALIEXPRESS',
                                    'BARBERSHOP',]
            ,'entertainment':      ['BILLIARDS','NEWROADS PERFORMING','AXE THROWING', 'FISH AND WILDLI', 'BAIT', 'PPARK', 'CLUB' , 'USD','CINEPLEX','MOVIE THEATRE','THEATRE','DAVE', 'ELECTRIC',
                                    'FAMOUS PLAYER','MIRVISH']
            ,'travel':             ['MIAMI','AIRCANADA','RCL','COZUMEL','AIR CANADA','MIND PEOPLE', 'FLIGHT CENTRE','EXPEDIA','HALIFAX','PEGGYS COVE']
            ,'health':             ['PHARM','DRUG STORE','LA FITNESS','DR','MASSAGE','DENTIST','OPTOMETRIST','OPTICIAN','CLINIC','CVC','MEDICAL','HOSPITAL','HEALTH','WELLNESS',
                                    'MEMBERSHIP FEE INSTALLMENT','WATER DEPOT']
            ,'utilities':          ['BELL ','ROGERS','HYDRO ONE','TELMAX']
            ,'weed and alcohol':   ['LCBO','BEER STORE','WINE','LIQUOR','WOODS','NSLC','CANNAB','FIKA']
            ,'transportation':     ['TTC','TRANSIT' ,'VIA RAIL','TAXI','UBER','LYFT', 'PRESTO', 'PARKING', 'GREENP']
            ,'CREDIT CARD PAYMENT':['PAYMENT THANK YOU','PAYMENT RECEIVED','CREDIT ADJUSTMENT', 'BILL PAYMENT VISA', 'BILL PAYMENT MASTERCARD','PAYMENTS American Express','Payment to  CIBC MASTERCARD']
            ,'GOVERNMENT':         ['EFT CREDIT','Town of Newma','NEWMARKET TAX', "CARBON REBATE"]
            ,'HELEN':              ['PETSMART','PETVALU','PET SERVICES']
            ,'GAMBLING':           ['BET365','FANDUEL', 'BETMGM','OLG']
            ,'DON HOWARDS':        ['DON HOWARD']
            ,'mortgage':           ['MORTGAGE']
            ,'e-transfer':         ['INTERAC E-TRANSFER SEND LISA AMENT','INTERAC E-TRANSFER RECEIVE','INTERAC E-TRANSFER SEND' ]
            ,'stocks':             ['QUESTRADE']
            ,'salary':             ['AYROLL DEPOSIT AMD','Direct deposit from AMD']
            ,'charity':            ['PLAN CANADA']
            ,'TRANSFERS IN/OUT':   ['TRANSFER IN', 'TRANSFER OUT', 'CHEQUE IMAGE DEPOSIT', 'INTEREST','ABM DEPOSIT','Card Load','Transfer from  Simplii','Referral Bonus','Account Credited']
            ,'uncategorized':      []
            }

# if windows:
# with open('C:\Documents\Python310\Scripts\bank_statement_csv_parser\cibc_costco_mastercard_04_2018_to_05_2025.csv' , mode='r') as file:
# if mac:

#filename= 'C:\Documents\Python310\Scripts\bank_statement_&_credit_card_csv_parser'
costco_mastercard_csv = r"account_or_credit_statements\cibc_costco_mastercard_04_2024_to_05_2025.csv"
simplii_checking_account = r'account_or_credit_statements\simplii_checking_may_2024_to_may_2025.csv'
amex_cobalt = r"account_or_credit_statements\amex_cobalt_till_05_10_2025.csv"
td_visa_aeroplan = r"account_or_credit_statements\td_visa_dec_2024_to_jan_2025.csv"
eq_bank_account = r"account_or_credit_statements\eq_bank_account_april_2025_to_may_10_2025.csv"

#filename= 'C:\Documents\Python310\Scripts\bank_statement_csv_parser\cibc_costco_mastercard_04_2018_to_05_2025.csv'

############################## END VARIABLE DECLARATIONS END ##############################################################################

##################################### MAIN ################################################################

files_with_types = [
    (costco_mastercard_csv, 'cibc'),
    (simplii_checking_account, 'simplii'),
    (amex_cobalt, 'amex'),
    (td_visa_aeroplan, "td"),
    (eq_bank_account,'eq')

    # Add as many as you want
]
parsed_purchases = my_functions.parse_multiple_csv(files_with_types)

#parse the CSV file purchases
#parsed_purchases = my_functions.parse_csv(costco_mastercard_csv,'cibc')

# Categorize the purchases
sorted_purchases = my_functions.categorize_purchases(parsed_purchases, categories)
print("\n",len(sorted_purchases['uncategorized']), "Out of", len(parsed_purchases), "Uncatageroized purchases", "\n")
print(f"uncategorized purchases are: \n {sorted_purchases['uncategorized']}")
#let user choose and create own categories
# final_purchases, final_categories = my_functions.review_uncategorized_purchases(
#     sorted_purchases, parsed_purchases, categories
# )
# print(f"New sorted purchases are ${final_purchases} and the New Categories are: ${final_categories}")


#Print the sum of the purchases in each category
total_spent, grand_total, credit_payment, total_credit_pay, returns= 0,0,0,0,0
for category, purchases in sorted_purchases.items():
    for purchase in purchases:
        if purchase['debit'] < 0:  # Check if the purchase is a debit (negative value) 
            if category != 'CREDIT CARD PAYMENT' or  category != 'E-TRANSFER':
                returns+= purchase['debit']  # Add to returns
        else:
            total_spent += purchase['debit']
    grand_total += total_spent  # Add to grand total
    total_credit_pay += credit_payment  # Add to total CREDIT CARD PAYMENT
    #print(f"{category:>25} - Total Spent: ${total_spent:<10.2f} Credit: ${credit_payment:<10.2f}") 
    result_string += "{:<25}".format(category) + " - Total Spent:   $" + "{:<15.2f}".format(total_spent) + "  Credit:   $" + "{:<15.2f}".format(credit_payment) + "\n"
    total_spent = 0  # Reset total_spent for the next category
    credit_payment = 0  # Reset credit_payment for the next category
print(f"\n==> Grand Total Spent: ${grand_total:<10.2f} Total Returns: ${returns:<10.2f} Total CREDIT CARD PAYMENT: ${total_credit_pay:<10.2f}\n")
result_string += "\n==> Grand Total Spent: ${:<10.2f}".format(grand_total) + "Total Returns: ${:^20.2f}".format(returns) + " Total CREDIT CARD PAYMENT: ${:^20.2f}".format(total_credit_pay) + "\n"

most_used, sub_sums, sub_counts = my_functions.analyze_category_keywords(sorted_purchases, categories)
# for cat in categories:
#     print(f"\nCategory: {cat}")
#     print(f"  Most-used keyword: {most_used[cat][0]} ({most_used[cat][1]} times)")
#     print("  Keyword breakdown:")
#     for kw in sub_counts[cat]:
#         print(f"    {kw:<15} - Count: {sub_counts[cat][kw]:<3}  Sum: ${sub_sums[cat][kw]:.2f}")


# Build your summary string as you would print it
summary_text = ""
#summary_text += f"{len(sorted_purchases['uncategorized'])} out of {len(parsed_purchases)} Uncatageroized purchases\n"
#summary_text += f"\n==> Grand Total Spent: ${grand_total:<10.2f} Total Returns: ${returns:^20.2f} Total CREDIT CARD PAYMENT: ${total_credit_pay:^20.2f}\n"

# Now call the main window function

summary_text = my_functions.build_summary_string(categories, sorted_purchases, parsed_purchases, grand_total, returns, total_credit_pay)
summary_text = "" 

my_functions.show_main_window(
    categories,
    sorted_purchases,
    most_used,
    sub_sums,
    sub_counts,
    summary_text,
    grand_total,
    returns,
    total_credit_pay,
    parsed_purchases
)