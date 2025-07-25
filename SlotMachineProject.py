import streamlit as st
import random
import json
import os

# --- Slot Machine Logic ---
MAX_LINES = 3
MAX_BET = 100
MIN_BET = 1
ROWS = 3
COLS = 3

symbol_count = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8
}
symbol_value = {
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2
}
USERS_FILE = "users.json"

def check_winnings(columns, lines, bet, values):
    winnings = 0
    winning_lines = []
    for line in range(lines):
        symbol = columns[0][line]
        for column in columns:
            symbol_to_check = column[line]
            if symbol != symbol_to_check:
                break
        else:
            winnings += values[symbol] * bet
            winning_lines.append(line + 1)
    return winnings, winning_lines

def get_slot_machine_spin(rows, cols, symbols):
    all_symbols = []
    for symbol, symbol_count in symbols.items():
        for _ in range(symbol_count):
            all_symbols.append(symbol)
    columns = []
    for _ in range(cols):
        column = []
        current_symbols = all_symbols[:]
        for _ in range(rows):
            value = random.choice(current_symbols)
            current_symbols.remove(value)
            column.append(value)
        columns.append(column)
    return columns

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# --- Streamlit App ---

st.set_page_config(page_title="Slot Machine", page_icon="🎰", layout="centered")

st.markdown(
    "<h1 style='text-align: center; color: gold; font-family: Impact;'>🎰 SLOT MACHINE 🎰</h1>",
    unsafe_allow_html=True,
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "balance" not in st.session_state:
    st.session_state.balance = 0

users = load_users()

def login(username, password):
    if username in users and users[username]["password"] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.balance = users[username]["balance"]
        st.success("Logged in successfully!")
    else:
        st.error("Invalid username or password.")

def register(username, password):
    if not username or not password:
        st.error("Username and password cannot be empty.")
        return
    if username in users:
        st.error("Username already exists.")
        return
    users[username] = {"password": password, "balance": 0}
    save_users(users)
    st.success("Registration successful! Please log in.")

def save_balance():
    users[st.session_state.username]["balance"] = st.session_state.balance
    save_users(users)

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            login(login_username, login_password)
    with tab2:
        reg_username = st.text_input("New Username", key="reg_user")
        reg_password = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            register(reg_username, reg_password)
    st.stop()

# --- Main Game UI ---

st.markdown(f"<h3 style='color: #39FF14;'>Welcome, {st.session_state.username}!</h3>", unsafe_allow_html=True)
st.markdown(f"<h4 style='color: gold;'>Balance: ${st.session_state.balance}</h4>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    deposit_amount = st.number_input("Deposit Amount", min_value=1, value=100, step=1)
    if st.button("Deposit"):
        st.session_state.balance += deposit_amount
        save_balance()
        st.success(f"Deposited ${deposit_amount}.")

with col2:
    if st.button("Logout"):
        save_balance()
        st.session_state.logged_in = False
        st.experimental_rerun()

st.divider()

with st.form("spin_form"):
    lines = st.number_input("Lines (1-3)", min_value=1, max_value=3, value=1, step=1)
    bet = st.number_input("Bet per line", min_value=MIN_BET, max_value=MAX_BET, value=1, step=1)
    spin_btn = st.form_submit_button("SPIN 🎰")

    if spin_btn:
        total_bet = lines * bet
        if total_bet > st.session_state.balance:
            st.error("Not enough balance for this bet.")
        else:
            slots = get_slot_machine_spin(ROWS, COLS, symbol_count)
            # Show slot grid
            slot_colors = {"A": "gold", "B": "deepskyblue", "C": "hotpink", "D": "limegreen"}
            st.markdown("<h2 style='text-align:center;'>Result:</h2>", unsafe_allow_html=True)
            for r in range(ROWS):
                row_symbols = []
                for c in range(COLS):
                    sym = slots[c][r]
                    color = slot_colors.get(sym, "white")
                    row_symbols.append(f"<span style='font-size:2em; color:{color}; font-family:Impact;'>{sym}</span>")
                st.markdown(
                    "<div style='text-align:center;'>" + " &nbsp; ".join(row_symbols) + "</div>",
                    unsafe_allow_html=True,
                )
            winnings, winning_lines = check_winnings(slots, lines, bet, symbol_value)
            st.session_state.balance += winnings - total_bet
            save_balance()
            if winnings > 0:
                st.success(f"You won ${winnings} on lines: {', '.join(map(str, winning_lines))}!")
            else:
                st.info("No win. Try again!")
            st.markdown(f"<h4 style='color: gold;'>Balance: ${st.session_state.balance}</h4>", unsafe_allow_html=True)